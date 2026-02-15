from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from apps.fiscal.forms import ExpenseForm
from apps.fiscal.models import Expense
from apps.fiscal.models import ExpenseCategory
from apps.invoicing.services.permissions import require_business


@login_required
@require_business
def expense_list(request):
    """List all expenses with filters."""
    expenses = Expense.objects.filter(
        business_profile=request.business,
    ).order_by("-date")

    # Filter by year
    year = request.GET.get("year")
    if year:
        expenses = expenses.filter(date__year=year)

    # Filter by quarter
    quarter = request.GET.get("quarter")
    if quarter:
        quarter = int(quarter)
        if quarter == 1:
            expenses = expenses.filter(date__month__in=[1, 2, 3])
        elif quarter == 2:
            expenses = expenses.filter(date__month__in=[4, 5, 6])
        elif quarter == 3:
            expenses = expenses.filter(date__month__in=[7, 8, 9])
        elif quarter == 4:
            expenses = expenses.filter(date__month__in=[10, 11, 12])

    # Filter by category
    category = request.GET.get("category")
    if category:
        expenses = expenses.filter(category=category)

    # Pagination
    paginator = Paginator(expenses, 25)
    page = request.GET.get("page")
    expenses = paginator.get_page(page)

    # Get distinct years for filter dropdown
    years = Expense.objects.filter(business_profile=request.business).dates(
        "date", "year", order="DESC"
    )

    return render(
        request,
        "fiscal/expense/list.html",
        {
            "active_section": "fiscal_expenses",
            "business": request.business,
            "expenses": expenses,
            "years": [d.year for d in years],
            "categories": ExpenseCategory.choices,
            "current_filters": {
                "year": year,
                "quarter": quarter,
                "category": category,
            },
        },
    )


@login_required
@require_business
def expense_create(request):
    """Create a new expense."""
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.business_profile = request.business
            expense.save()
            messages.success(request, "Gasto creado.")
            return redirect("fiscal:expense_list")
    else:
        form = ExpenseForm()

    return render(
        request,
        "fiscal/expense/create.html",
        {
            "active_section": "fiscal_expenses",
            "business": request.business,
            "form": form,
        },
    )


@login_required
@require_business
def expense_edit(request, pk: int):
    """Edit an expense."""
    expense = get_object_or_404(
        Expense,
        pk=pk,
        business_profile=request.business,
    )

    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Gasto actualizado.")
            return redirect("fiscal:expense_list")
    else:
        form = ExpenseForm(instance=expense)

    return render(
        request,
        "fiscal/expense/edit.html",
        {
            "active_section": "fiscal_expenses",
            "business": request.business,
            "expense": expense,
            "form": form,
        },
    )


@login_required
@require_business
def expense_delete(request, pk: int):
    """Delete an expense."""
    expense = get_object_or_404(
        Expense,
        pk=pk,
        business_profile=request.business,
    )

    if request.method == "POST":
        expense.delete()
        messages.success(request, "Gasto eliminado.")
        return redirect("fiscal:expense_list")

    return render(
        request,
        "fiscal/expense/delete.html",
        {
            "active_section": "fiscal_expenses",
            "business": request.business,
            "expense": expense,
        },
    )
