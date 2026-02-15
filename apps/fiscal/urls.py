from django.urls import path

from apps.fiscal.views import expense_create
from apps.fiscal.views import expense_delete
from apps.fiscal.views import expense_edit
from apps.fiscal.views import expense_list
from apps.fiscal.views import fiscal_dashboard
from apps.fiscal.views import fiscal_year_create
from apps.fiscal.views import fiscal_year_detail
from apps.fiscal.views import fiscal_year_edit
from apps.fiscal.views import fiscal_year_list
from apps.fiscal.views import quarter_close
from apps.fiscal.views import quarter_detail
from apps.fiscal.views import quarter_save_result

app_name = "fiscal"

urlpatterns = [
    # Dashboard
    path("", fiscal_dashboard, name="dashboard"),
    # Fiscal years
    path("anos/", fiscal_year_list, name="fiscal_year_list"),
    path("anos/nuevo/", fiscal_year_create, name="fiscal_year_create"),
    path("anos/<int:year>/", fiscal_year_detail, name="fiscal_year_detail"),
    path("anos/<int:year>/editar/", fiscal_year_edit, name="fiscal_year_edit"),
    # Quarters
    path(
        "anos/<int:year>/t/<int:quarter_num>/",
        quarter_detail,
        name="quarter_detail",
    ),
    path(
        "anos/<int:year>/t/<int:quarter_num>/guardar/",
        quarter_save_result,
        name="quarter_save_result",
    ),
    path(
        "anos/<int:year>/t/<int:quarter_num>/cerrar/",
        quarter_close,
        name="quarter_close",
    ),
    # Expenses
    path("gastos/", expense_list, name="expense_list"),
    path("gastos/nuevo/", expense_create, name="expense_create"),
    path("gastos/<int:pk>/editar/", expense_edit, name="expense_edit"),
    path("gastos/<int:pk>/eliminar/", expense_delete, name="expense_delete"),
]
