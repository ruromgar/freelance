from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from apps.invoicing.models.business import BusinessMembership
from apps.invoicing.models.business import BusinessProfile
from apps.invoicing.models.client import Client
from apps.invoicing.models.invoice import Invoice
from apps.invoicing.models.invoice import InvoiceLineItem
from apps.invoicing.models.payment import Payment
from apps.invoicing.services.payment import check_and_update_invoice_status
from apps.invoicing.services.payment import get_invoice_balance
from apps.invoicing.services.payment import get_invoice_paid_amount


class PaymentServiceTestCase(TestCase):
    def setUp(self):
        self.bp = BusinessProfile.objects.create(name="Test", tax_id="B123")
        self.client_obj = Client.objects.create(business_profile=self.bp, name="Acme")
        self.invoice = Invoice.objects.create(
            business_profile=self.bp,
            client=self.client_obj,
            number="F-2026-00001",
            issue_date="2026-01-01",
            status=Invoice.Status.SENT,
        )
        InvoiceLineItem.objects.create(
            invoice=self.invoice,
            description="Service",
            quantity=Decimal("1"),
            unit_price=Decimal("1000"),
            tax_rate=Decimal("21"),
        )

    def test_get_invoice_paid_amount(self):
        self.assertEqual(get_invoice_paid_amount(self.invoice), Decimal("0"))
        Payment.objects.create(
            invoice=self.invoice,
            amount=Decimal("500"),
            date="2026-01-15",
        )
        self.assertEqual(get_invoice_paid_amount(self.invoice), Decimal("500"))

    def test_get_invoice_balance(self):
        self.assertEqual(
            get_invoice_balance(self.invoice), Decimal("1210")
        )  # 1000 + 21% IVA
        Payment.objects.create(
            invoice=self.invoice,
            amount=Decimal("500"),
            date="2026-01-15",
        )
        self.assertEqual(get_invoice_balance(self.invoice), Decimal("710"))

    def test_auto_mark_paid_when_full_payment(self):
        Payment.objects.create(
            invoice=self.invoice,
            amount=Decimal("1210"),
            date="2026-01-15",
        )
        check_and_update_invoice_status(self.invoice)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.PAID)

    def test_auto_mark_paid_with_partial_payments(self):
        Payment.objects.create(
            invoice=self.invoice,
            amount=Decimal("600"),
            date="2026-01-10",
        )
        check_and_update_invoice_status(self.invoice)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.SENT)

        Payment.objects.create(
            invoice=self.invoice,
            amount=Decimal("610"),
            date="2026-01-20",
        )
        check_and_update_invoice_status(self.invoice)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.PAID)

    def test_revert_paid_status_when_payment_deleted(self):
        payment = Payment.objects.create(
            invoice=self.invoice,
            amount=Decimal("1210"),
            date="2026-01-15",
        )
        check_and_update_invoice_status(self.invoice)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.PAID)

        payment.delete()
        check_and_update_invoice_status(self.invoice)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.SENT)


class PaymentViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("owner", password="test")
        self.bp = BusinessProfile.objects.create(name="Test", tax_id="B123")
        BusinessMembership.objects.create(
            user=self.user,
            business_profile=self.bp,
            role=BusinessMembership.Role.OWNER,
        )
        self.client_obj = Client.objects.create(business_profile=self.bp, name="Acme")
        self.invoice = Invoice.objects.create(
            business_profile=self.bp,
            client=self.client_obj,
            number="F-2026-00001",
            issue_date="2026-01-01",
            status=Invoice.Status.SENT,
        )
        InvoiceLineItem.objects.create(
            invoice=self.invoice,
            description="Service",
            quantity=Decimal("1"),
            unit_price=Decimal("1000"),
            tax_rate=Decimal("21"),
        )
        self.client.login(username="owner", password="test")
        session = self.client.session
        session["active_business_id"] = self.bp.pk
        session.save()

    def test_payment_list(self):
        response = self.client.get("/pagos/")
        self.assertEqual(response.status_code, 200)

    def test_payment_create_for_invoice(self):
        response = self.client.post(
            f"/facturas/{self.invoice.pk}/pago/",
            {
                "amount": "1210",
                "date": "2026-01-15",
                "method": "transfer",
                "notes": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, Invoice.Status.PAID)
        self.assertEqual(Payment.objects.count(), 1)
