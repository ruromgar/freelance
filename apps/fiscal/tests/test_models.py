from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from apps.fiscal.models import Expense
from apps.fiscal.models import ExpenseCategory
from apps.fiscal.models import FiscalYear
from apps.fiscal.models import VATType
from apps.invoicing.models import BusinessProfile


class FiscalYearModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@test.com", "pass")
        self.business = BusinessProfile.objects.create(
            name="Test Business",
            tax_id="B12345678",
        )

    def test_create_fiscal_year(self):
        fy = FiscalYear.objects.create(
            business_profile=self.business,
            year=2026,
        )
        self.assertEqual(str(fy), "2026")

    def test_create_quarters(self):
        fy = FiscalYear.objects.create(
            business_profile=self.business,
            year=2026,
        )
        fy.create_quarters()
        self.assertEqual(fy.quarters.count(), 4)

    def test_unique_year_per_business(self):
        FiscalYear.objects.create(business_profile=self.business, year=2026)
        with self.assertRaises(Exception):
            FiscalYear.objects.create(business_profile=self.business, year=2026)


class QuarterModelTest(TestCase):
    def setUp(self):
        self.business = BusinessProfile.objects.create(
            name="Test Business",
            tax_id="B12345678",
        )
        self.fy = FiscalYear.objects.create(
            business_profile=self.business,
            year=2026,
        )
        self.fy.create_quarters()

    def test_quarter_date_range_q1(self):
        q1 = self.fy.quarters.get(number=1)
        start, end = q1.get_date_range()
        self.assertEqual(start, date(2026, 1, 1))
        self.assertEqual(end, date(2026, 3, 31))

    def test_quarter_date_range_q2(self):
        q2 = self.fy.quarters.get(number=2)
        start, end = q2.get_date_range()
        self.assertEqual(start, date(2026, 4, 1))
        self.assertEqual(end, date(2026, 6, 30))

    def test_quarter_date_range_q3(self):
        q3 = self.fy.quarters.get(number=3)
        start, end = q3.get_date_range()
        self.assertEqual(start, date(2026, 7, 1))
        self.assertEqual(end, date(2026, 9, 30))

    def test_quarter_date_range_q4(self):
        q4 = self.fy.quarters.get(number=4)
        start, end = q4.get_date_range()
        self.assertEqual(start, date(2026, 10, 1))
        self.assertEqual(end, date(2026, 12, 31))


class ExpenseModelTest(TestCase):
    def setUp(self):
        self.business = BusinessProfile.objects.create(
            name="Test Business",
            tax_id="B12345678",
        )

    def test_expense_vat_calculation(self):
        expense = Expense.objects.create(
            business_profile=self.business,
            date=date(2026, 1, 15),
            concept="Software subscription",
            category=ExpenseCategory.SOFTWARE,
            taxable_base=Decimal("100.00"),
            vat_type=VATType.GENERAL,
        )
        self.assertEqual(expense.input_vat, Decimal("21.00"))
        self.assertEqual(expense.total, Decimal("121.00"))

    def test_expense_exempt_vat(self):
        expense = Expense.objects.create(
            business_profile=self.business,
            date=date(2026, 1, 15),
            concept="Social security",
            category=ExpenseCategory.SOCIAL_SECURITY,
            taxable_base=Decimal("300.00"),
            vat_type=VATType.EXEMPT,
        )
        self.assertEqual(expense.input_vat, Decimal("0.00"))
        self.assertEqual(expense.total, Decimal("300.00"))

    def test_expense_get_quarter(self):
        fy = FiscalYear.objects.create(business_profile=self.business, year=2026)
        fy.create_quarters()

        expense = Expense.objects.create(
            business_profile=self.business,
            date=date(2026, 2, 15),
            concept="Test",
            taxable_base=Decimal("100.00"),
        )
        quarter = expense.get_quarter()
        self.assertEqual(quarter.number, 1)
