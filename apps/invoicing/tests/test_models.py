from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from apps.invoicing.models.business import BusinessMembership
from apps.invoicing.models.business import BusinessProfile
from apps.invoicing.models.business import InvoiceNumbering
from apps.invoicing.models.business import InvoiceTheme
from apps.invoicing.models.client import Client
from apps.invoicing.models.invoice import Invoice
from apps.invoicing.models.invoice import InvoiceLineItem


class BusinessProfileTestCase(TestCase):
    def test_create_business_profile(self):
        bp = BusinessProfile.objects.create(name="Test SL", tax_id="B12345678")
        self.assertEqual(str(bp), "Test SL")
        self.assertEqual(bp.country, "ES")
        self.assertEqual(bp.default_currency, "EUR")


class BusinessMembershipTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="test")
        self.bp = BusinessProfile.objects.create(name="Test SL", tax_id="B12345678")

    def test_create_membership(self):
        m = BusinessMembership.objects.create(
            user=self.user,
            business_profile=self.bp,
            role=BusinessMembership.Role.OWNER,
        )
        self.assertEqual(m.role, "owner")

    def test_unique_together(self):
        BusinessMembership.objects.create(
            user=self.user,
            business_profile=self.bp,
            role=BusinessMembership.Role.OWNER,
        )
        with self.assertRaises(Exception):
            BusinessMembership.objects.create(
                user=self.user,
                business_profile=self.bp,
                role=BusinessMembership.Role.EDITOR,
            )


class InvoiceNumberingTestCase(TestCase):
    def test_generate_number(self):
        bp = BusinessProfile.objects.create(name="Test", tax_id="B123")
        numbering = InvoiceNumbering.objects.create(
            business_profile=bp, series_prefix="F", next_number=1
        )
        number = numbering.generate_number(2026)
        self.assertEqual(number, "F-2026-00001")
        self.assertEqual(numbering.next_number, 2)
        number2 = numbering.generate_number(2026)
        self.assertEqual(number2, "F-2026-00002")


class InvoiceThemeTestCase(TestCase):
    def test_default_theme_exclusivity(self):
        bp = BusinessProfile.objects.create(name="Test", tax_id="B123")
        t1 = InvoiceTheme.objects.create(
            business_profile=bp, name="Theme 1", is_default=True
        )
        t2 = InvoiceTheme.objects.create(
            business_profile=bp, name="Theme 2", is_default=True
        )
        t1.refresh_from_db()
        self.assertFalse(t1.is_default)
        self.assertTrue(t2.is_default)


class InvoiceLineItemTestCase(TestCase):
    def setUp(self):
        self.bp = BusinessProfile.objects.create(name="Test", tax_id="B123")
        self.client = Client.objects.create(business_profile=self.bp, name="Client")
        self.invoice = Invoice.objects.create(
            business_profile=self.bp,
            client=self.client,
            number="F-2026-00001",
            issue_date="2026-01-01",
        )

    def test_line_item_calculations(self):
        line = InvoiceLineItem.objects.create(
            invoice=self.invoice,
            description="Service",
            quantity=Decimal("10"),
            unit_price=Decimal("100"),
            tax_rate=Decimal("21"),
            withholding_rate=Decimal("15"),
            discount_percent=Decimal("10"),
        )
        # subtotal: 10 * 100 * (1 - 0.10) = 900
        self.assertEqual(line.subtotal, Decimal("900.00"))
        # tax: 900 * 0.21 = 189
        self.assertEqual(line.tax_amount, Decimal("189.00"))
        # withholding: 900 * 0.15 = 135
        self.assertEqual(line.withholding_amount, Decimal("135.00"))
        # line_total: 900 + 189 - 135 = 954
        self.assertEqual(line.line_total, Decimal("954.00"))

    def test_invoice_totals(self):
        InvoiceLineItem.objects.create(
            invoice=self.invoice,
            description="Service A",
            quantity=Decimal("1"),
            unit_price=Decimal("1000"),
            tax_rate=Decimal("21"),
            withholding_rate=Decimal("15"),
        )
        InvoiceLineItem.objects.create(
            invoice=self.invoice,
            description="Service B",
            quantity=Decimal("2"),
            unit_price=Decimal("500"),
            tax_rate=Decimal("10"),
            withholding_rate=Decimal("0"),
        )
        # A: subtotal=1000, tax=210, withholding=150
        # B: subtotal=1000, tax=100, withholding=0
        self.assertEqual(self.invoice.subtotal, Decimal("2000"))
        self.assertEqual(self.invoice.tax_total, Decimal("310"))
        self.assertEqual(self.invoice.withholding_total, Decimal("150"))
        self.assertEqual(self.invoice.total, Decimal("2160"))


class PermissionsTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="test")
        self.viewer = User.objects.create_user("viewer", password="test")
        self.bp = BusinessProfile.objects.create(name="Test SL", tax_id="B12345678")
        BusinessMembership.objects.create(
            user=self.owner,
            business_profile=self.bp,
            role=BusinessMembership.Role.OWNER,
        )
        BusinessMembership.objects.create(
            user=self.viewer,
            business_profile=self.bp,
            role=BusinessMembership.Role.VIEWER,
        )

    def test_owner_can_edit_business(self):
        self.client.login(username="owner", password="test")
        self.client.get("/empresa/editar/")
        # Session gets set
        session = self.client.session
        session["active_business_id"] = self.bp.pk
        session.save()
        response = self.client.get("/empresa/editar/")
        self.assertEqual(response.status_code, 200)

    def test_viewer_cannot_edit_business(self):
        self.client.login(username="viewer", password="test")
        session = self.client.session
        session["active_business_id"] = self.bp.pk
        session.save()
        response = self.client.get("/empresa/editar/")
        self.assertEqual(response.status_code, 404)
