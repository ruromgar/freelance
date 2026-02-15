from apps.fiscal.views.dashboard import fiscal_dashboard
from apps.fiscal.views.expense import expense_create
from apps.fiscal.views.expense import expense_delete
from apps.fiscal.views.expense import expense_edit
from apps.fiscal.views.expense import expense_list
from apps.fiscal.views.fiscal_year import fiscal_year_create
from apps.fiscal.views.fiscal_year import fiscal_year_detail
from apps.fiscal.views.fiscal_year import fiscal_year_edit
from apps.fiscal.views.fiscal_year import fiscal_year_list
from apps.fiscal.views.quarter import quarter_close
from apps.fiscal.views.quarter import quarter_detail
from apps.fiscal.views.quarter import quarter_save_result

__all__ = [
    "expense_create",
    "expense_delete",
    "expense_edit",
    "expense_list",
    "fiscal_dashboard",
    "fiscal_year_create",
    "fiscal_year_detail",
    "fiscal_year_edit",
    "fiscal_year_list",
    "quarter_close",
    "quarter_detail",
    "quarter_save_result",
]
