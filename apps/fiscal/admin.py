from django.contrib import admin
from django.db.models import QuerySet
from django.db.models import Sum
from django.http import HttpRequest
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline

from apps.fiscal.models import Expense
from apps.fiscal.models import FiscalYear
from apps.fiscal.models import Quarter
from apps.fiscal.models import QuarterlyResult


class QuarterInline(TabularInline):
    model = Quarter
    extra = 0
    show_change_link = True
    fields = ("number", "closed", "closing_date")
    readonly_fields = ("closing_date",)


@admin.register(FiscalYear)
class FiscalYearAdmin(ModelAdmin):
    list_display = (
        "year",
        "business_profile",
        "estimation_type",
        "closed",
        "quarters_summary",
    )
    list_filter = ("business_profile", "closed", "estimation_type")
    search_fields = ("year", "business_profile__name")
    inlines = [QuarterInline]
    actions = ["close_fiscal_year", "create_quarters"]

    fieldsets = (
        (None, {"fields": ("business_profile", "year", "estimation_type", "closed")}),
        ("Notas", {"fields": ("notes",), "classes": ("collapse",)}),
    )

    @admin.display(description="Trimestres")
    def quarters_summary(self, obj):
        total = obj.quarters.count()
        closed = obj.quarters.filter(closed=True).count()
        if total == 0:
            return "-"
        return f"{closed}/{total} cerrados"

    @admin.action(description="Crear trimestres (si no existen)")
    def create_quarters(self, request: HttpRequest, queryset: QuerySet):
        for fiscal_year in queryset:
            fiscal_year.create_quarters()
        self.message_user(
            request, f"Trimestres creados para {queryset.count()} año(s)."
        )

    @admin.action(description="Cerrar año fiscal")
    def close_fiscal_year(self, request: HttpRequest, queryset: QuerySet):
        from django.contrib import messages

        closed = 0
        for fiscal_year in queryset:
            quarters = fiscal_year.quarters.all()
            if quarters.count() < 4:
                self.message_user(
                    request,
                    f"El año {fiscal_year.year} no tiene los 4 trimestres.",
                    messages.WARNING,
                )
                continue
            if quarters.filter(closed=False).exists():
                self.message_user(
                    request,
                    f"El año {fiscal_year.year} tiene trimestres sin cerrar.",
                    messages.WARNING,
                )
                continue
            fiscal_year.closed = True
            fiscal_year.save()
            closed += 1

        if closed:
            self.message_user(request, f"Cerrados {closed} año(s) fiscal(es).")


@admin.register(Quarter)
class QuarterAdmin(ModelAdmin):
    list_display = (
        "__str__",
        "fiscal_year__business_profile",
        "closed",
        "total_expenses",
        "has_result",
    )
    list_filter = ("fiscal_year__business_profile", "fiscal_year", "number", "closed")
    search_fields = ("fiscal_year__year", "fiscal_year__business_profile__name")
    actions = ["calculate_and_save_result", "close_quarter"]

    fieldsets = (
        (None, {"fields": ("fiscal_year", "number")}),
        ("Estado", {"fields": ("closed", "closing_date")}),
        ("Notas", {"fields": ("notes",), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("fiscal_year", "fiscal_year__business_profile")

    @admin.display(description="Empresa")
    def fiscal_year__business_profile(self, obj):
        return obj.fiscal_year.business_profile.name

    @admin.display(description="Gastos")
    def total_expenses(self, obj):
        total = Expense.objects.filter(
            business_profile=obj.fiscal_year.business_profile,
            date__range=obj.get_date_range(),
        ).aggregate(total=Sum("taxable_base"))["total"]
        if total:
            return f"{total:,.2f}€"
        return "-"

    @admin.display(description="Resultado", boolean=True)
    def has_result(self, obj):
        return hasattr(obj, "result")

    @admin.action(description="Calcular y guardar resultado (303 + 130)")
    def calculate_and_save_result(self, request: HttpRequest, queryset: QuerySet):
        from apps.fiscal.services import calculate_modelo_130
        from apps.fiscal.services import calculate_modelo_303

        for quarter in queryset:
            result_303 = calculate_modelo_303(quarter)
            result_130 = calculate_modelo_130(quarter)

            QuarterlyResult.objects.update_or_create(
                quarter=quarter,
                defaults={
                    "modelo_303_calculated": result_303["result"],
                    "modelo_130_calculated": result_130["result"],
                },
            )
        self.message_user(
            request,
            f"Calculado resultado para {queryset.count()} trimestre(s).",
        )

    @admin.action(description="Cerrar trimestre")
    def close_quarter(self, request: HttpRequest, queryset: QuerySet):
        from django.contrib import messages
        from django.utils import timezone

        closed = 0
        for quarter in queryset:
            if not hasattr(quarter, "result"):
                self.message_user(
                    request,
                    f"El trimestre {quarter} no tiene resultado calculado.",
                    messages.WARNING,
                )
                continue
            quarter.closed = True
            quarter.closing_date = timezone.now().date()
            quarter.save()
            closed += 1

        if closed:
            self.message_user(request, f"Cerrados {closed} trimestre(s).")


@admin.register(Expense)
class ExpenseAdmin(ModelAdmin):
    list_display = (
        "date",
        "concept",
        "business_profile",
        "category",
        "taxable_base",
        "vat_type_display",
        "input_vat",
        "deductibility_display",
    )
    list_filter = (
        "business_profile",
        "category",
        "vat_deductible",
        "irpf_deductible",
    )
    search_fields = ("concept", "supplier", "reference", "business_profile__name")
    date_hierarchy = "date"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "business_profile",
                    "date",
                    "concept",
                    "supplier",
                    "reference",
                    "category",
                )
            },
        ),
        (
            "Importes",
            {"fields": ("taxable_base", "vat_type", "input_vat")},
        ),
        (
            "Deducibilidad",
            {"fields": ("irpf_deductible", "vat_deductible")},
        ),
        ("Notas", {"fields": ("notes",), "classes": ("collapse",)}),
    )
    readonly_fields = ("input_vat",)

    @admin.display(description="IVA")
    def vat_type_display(self, obj):
        return f"{obj.vat_type}%"

    @admin.display(description="Deducible")
    def deductibility_display(self, obj):
        parts = []
        if obj.irpf_deductible:
            parts.append("IRPF")
        if obj.vat_deductible:
            parts.append("IVA")
        if parts:
            return format_html(
                '<span style="color: green;">{}</span>',
                " + ".join(parts),
            )
        return format_html('<span style="color: gray;">No</span>')


@admin.register(QuarterlyResult)
class QuarterlyResultAdmin(ModelAdmin):
    list_display = (
        "quarter",
        "quarter__business_profile",
        "modelo_303_display",
        "modelo_130_display",
        "submission_date",
    )
    list_filter = ("quarter__fiscal_year__business_profile", "quarter__fiscal_year")
    search_fields = (
        "quarter__fiscal_year__year",
        "quarter__fiscal_year__business_profile__name",
    )

    fieldsets = (
        (None, {"fields": ("quarter",)}),
        (
            "Modelo 303 (IVA)",
            {"fields": ("modelo_303_calculated", "modelo_303_submitted")},
        ),
        (
            "Modelo 130 (IRPF)",
            {"fields": ("modelo_130_calculated", "modelo_130_submitted")},
        ),
        (
            "Presentación",
            {"fields": ("submission_date", "notes")},
        ),
    )

    @admin.display(description="Empresa")
    def quarter__business_profile(self, obj):
        return obj.quarter.fiscal_year.business_profile.name

    @admin.display(description="Modelo 303")
    def modelo_303_display(self, obj):
        calc = obj.modelo_303_calculated
        sub = obj.modelo_303_submitted
        color = "green" if calc >= 0 else "red"
        result = format_html(
            '<span style="color: {};">{:+,.2f}€</span>',
            color,
            calc,
        )
        if sub is not None:
            result += f" (presentado: {sub:+,.2f}€)"
        return result

    @admin.display(description="Modelo 130")
    def modelo_130_display(self, obj):
        calc = obj.modelo_130_calculated
        sub = obj.modelo_130_submitted
        result = f"{calc:,.2f}€"
        if sub is not None:
            result += f" (presentado: {sub:,.2f}€)"
        return result
