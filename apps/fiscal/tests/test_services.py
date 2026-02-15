from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from apps.fiscal.models import Expense
from apps.fiscal.models import ExpenseCategory
from apps.fiscal.models import FiscalYear
from apps.fiscal.models import VATType
from apps.fiscal.services import calculate_modelo_130
from apps.fiscal.services import calculate_modelo_303
from apps.invoicing.models import BusinessMembership
from apps.invoicing.models import BusinessProfile
from apps.invoicing.models import Client
from apps.invoicing.models import Invoice
from apps.invoicing.models import InvoiceLineItem


class Modelo303Test(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@test.com", "pass")
        self.business = BusinessProfile.objects.create(
            name="Test Business",
            tax_id="B12345678",
        )
        BusinessMembership.objects.create(
            user=self.user,
            business_profile=self.business,
            role=BusinessMembership.Role.OWNER,
        )
        self.client = Client.objects.create(
            business_profile=self.business,
            name="Test Client",
            tax_id="A12345678",
        )
        self.fy = FiscalYear.objects.create(
            business_profile=self.business,
            year=2026,
        )
        self.fy.create_quarters()
        self.q1 = self.fy.quarters.get(number=1)

    def test_modelo_303_no_data(self):
        result = calculate_modelo_303(self.q1)
        self.assertEqual(result["total_output_vat"], Decimal("0"))
        self.assertEqual(result["total_input_vat"], Decimal("0"))
        self.assertEqual(result["result"], Decimal("0"))

    def test_modelo_303_with_invoice(self):
        invoice = Invoice.objects.create(
            business_profile=self.business,
            client=self.client,
            number="F-2026-001",
            status=Invoice.Status.SENT,
            issue_date=date(2026, 2, 15),
        )
        InvoiceLineItem.objects.create(
            invoice=invoice,
            description="Service",
            quantity=1,
            unit_price=Decimal("1000.00"),
            tax_rate=Decimal("21.00"),
        )

        result = calculate_modelo_303(self.q1)
        self.assertEqual(result["total_output_vat"], Decimal("210.00"))
        self.assertEqual(result["result"], Decimal("210.00"))

    def test_modelo_303_with_expense(self):
        Expense.objects.create(
            business_profile=self.business,
            date=date(2026, 1, 15),
            concept="Software",
            taxable_base=Decimal("100.00"),
            vat_type=VATType.GENERAL,
            vat_deductible=True,
        )

        result = calculate_modelo_303(self.q1)
        self.assertEqual(result["total_input_vat"], Decimal("21.00"))
        self.assertEqual(result["result"], Decimal("-21.00"))

    def test_modelo_303_draft_invoice_excluded(self):
        invoice = Invoice.objects.create(
            business_profile=self.business,
            client=self.client,
            number="F-2026-001",
            status=Invoice.Status.DRAFT,
            issue_date=date(2026, 2, 15),
        )
        InvoiceLineItem.objects.create(
            invoice=invoice,
            description="Service",
            quantity=1,
            unit_price=Decimal("1000.00"),
            tax_rate=Decimal("21.00"),
        )

        result = calculate_modelo_303(self.q1)
        self.assertEqual(result["total_output_vat"], Decimal("0"))


class Modelo130Test(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@test.com", "pass")
        self.business = BusinessProfile.objects.create(
            name="Test Business",
            tax_id="B12345678",
        )
        BusinessMembership.objects.create(
            user=self.user,
            business_profile=self.business,
            role=BusinessMembership.Role.OWNER,
        )
        self.client = Client.objects.create(
            business_profile=self.business,
            name="Test Client",
            tax_id="A12345678",
        )
        self.fy = FiscalYear.objects.create(
            business_profile=self.business,
            year=2026,
            estimation_type="simplified",
        )
        self.fy.create_quarters()
        self.q1 = self.fy.quarters.get(number=1)

    def test_modelo_130_no_data(self):
        result = calculate_modelo_130(self.q1)
        self.assertEqual(result["accumulated_income"], Decimal("0"))
        self.assertEqual(result["result"], Decimal("0"))

    def test_modelo_130_with_income_and_expense(self):
        invoice = Invoice.objects.create(
            business_profile=self.business,
            client=self.client,
            number="F-2026-001",
            status=Invoice.Status.SENT,
            issue_date=date(2026, 2, 15),
        )
        InvoiceLineItem.objects.create(
            invoice=invoice,
            description="Service",
            quantity=1,
            unit_price=Decimal("1000.00"),
            tax_rate=Decimal("21.00"),
            withholding_rate=Decimal("15.00"),
        )

        Expense.objects.create(
            business_profile=self.business,
            date=date(2026, 1, 15),
            concept="Software",
            category=ExpenseCategory.SOFTWARE,
            taxable_base=Decimal("100.00"),
            irpf_deductible=True,
        )

        result = calculate_modelo_130(self.q1)
        self.assertEqual(result["accumulated_income"], Decimal("1000.00"))
        self.assertEqual(result["accumulated_expenses"], Decimal("100.00"))
        self.assertEqual(result["accumulated_withholdings"], Decimal("150.00"))
        # hard_to_justify = min(1000 * 0.05, 2000) = 50
        self.assertEqual(result["hard_to_justify_expenses"], Decimal("50.00"))
        # net_income = 1000 - 100 - 50 = 850
        self.assertEqual(result["net_income"], Decimal("850.00"))
        # gross_payment = 850 * 0.20 = 170
        self.assertEqual(result["gross_payment"], Decimal("170.00"))
        # result = max(170 - 150, 0) = 20
        self.assertEqual(result["result"], Decimal("20.00"))
