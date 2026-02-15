from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from apps.invoicing.models.business import BusinessMembership
from apps.invoicing.models.business import BusinessProfile
from apps.invoicing.models.client import Client
from apps.invoicing.models.invoice import Invoice
from apps.invoicing.models.invoice import InvoiceLineItem


class ClientViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("owner", password="test")
        self.bp = BusinessProfile.objects.create(name="Test SL", tax_id="B123")
        BusinessMembership.objects.create(
            user=self.user,
            business_profile=self.bp,
            role=BusinessMembership.Role.OWNER,
        )
        self.client.login(username="owner", password="test")
        session = self.client.session
        session["active_business_id"] = self.bp.pk
        session.save()

    def test_client_list(self):
        Client.objects.create(business_profile=self.bp, name="Acme")
        response = self.client.get("/clientes/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Acme")

    def test_client_create(self):
        response = self.client.post(
            "/clientes/nuevo/",
            {"name": "New Client", "tax_id": "A123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Client.objects.filter(name="New Client").exists())

    def test_client_search(self):
        Client.objects.create(business_profile=self.bp, name="Acme")
        Client.objects.create(business_profile=self.bp, name="Beta")
        response = self.client.get("/clientes/?q=Acme")
        self.assertContains(response, "Acme")
        self.assertNotContains(response, "Beta")


class InvoiceViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("owner", password="test")
        self.bp = BusinessProfile.objects.create(name="Test SL", tax_id="B123")
        BusinessMembership.objects.create(
            user=self.user,
            business_profile=self.bp,
            role=BusinessMembership.Role.OWNER,
        )
        self.test_client = Client.objects.create(business_profile=self.bp, name="Acme")
        self.client.login(username="owner", password="test")
        session = self.client.session
        session["active_business_id"] = self.bp.pk
        session.save()

    def test_invoice_list(self):
        response = self.client.get("/facturas/")
        self.assertEqual(response.status_code, 200)

    def test_invoice_create_and_auto_number(self):
        response = self.client.post(
            "/facturas/nueva/",
            {
                "client": self.test_client.pk,
                "issue_date": "2026-01-15",
                "currency": "EUR",
                "notes": "",
                "legal_text": "",
                "lines-TOTAL_FORMS": "1",
                "lines-INITIAL_FORMS": "0",
                "lines-MIN_NUM_FORMS": "0",
                "lines-MAX_NUM_FORMS": "1000",
                "lines-0-description": "Consulting",
                "lines-0-quantity": "10",
                "lines-0-unit_price": "100",
                "lines-0-tax_rate": "21",
                "lines-0-withholding_rate": "15",
                "lines-0-discount_percent": "0",
                "lines-0-position": "0",
            },
        )
        self.assertEqual(response.status_code, 302)
        invoice = Invoice.objects.first()
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.number, "F-2026-00001")
        self.assertEqual(invoice.status, "draft")

    def test_invoice_detail(self):
        invoice = Invoice.objects.create(
            business_profile=self.bp,
            client=self.test_client,
            number="F-2026-00001",
            issue_date="2026-01-01",
        )
        InvoiceLineItem.objects.create(
            invoice=invoice,
            description="Service",
            quantity=Decimal("1"),
            unit_price=Decimal("1000"),
            tax_rate=Decimal("21"),
        )
        response = self.client.get(f"/facturas/{invoice.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "F-2026-00001")
        self.assertContains(response, "1210,00")  # total (Spanish locale)

    def test_invoice_status_transition(self):
        invoice = Invoice.objects.create(
            business_profile=self.bp,
            client=self.test_client,
            number="F-2026-00001",
            issue_date="2026-01-01",
        )
        # draft -> sent
        self.client.post(f"/facturas/{invoice.pk}/estado/", {"status": "sent"})
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, "sent")
        # sent -> paid
        self.client.post(f"/facturas/{invoice.pk}/estado/", {"status": "paid"})
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, "paid")
        # paid -> draft (invalid)
        self.client.post(f"/facturas/{invoice.pk}/estado/", {"status": "draft"})
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, "paid")  # unchanged

    def test_draft_only_editing(self):
        invoice = Invoice.objects.create(
            business_profile=self.bp,
            client=self.test_client,
            number="F-2026-00001",
            issue_date="2026-01-01",
            status="sent",
        )
        response = self.client.get(f"/facturas/{invoice.pk}/editar/")
        self.assertEqual(response.status_code, 404)

    def test_cross_business_isolation(self):
        other_bp = BusinessProfile.objects.create(name="Other SL", tax_id="B999")
        other_client = Client.objects.create(
            business_profile=other_bp, name="Other Client"
        )
        other_invoice = Invoice.objects.create(
            business_profile=other_bp,
            client=other_client,
            number="X-2026-00001",
            issue_date="2026-01-01",
        )
        response = self.client.get(f"/facturas/{other_invoice.pk}/")
        self.assertEqual(response.status_code, 404)


class ExportViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("owner", password="test")
        self.bp = BusinessProfile.objects.create(name="Test SL", tax_id="B123")
        BusinessMembership.objects.create(
            user=self.user,
            business_profile=self.bp,
            role=BusinessMembership.Role.OWNER,
        )
        self.test_client = Client.objects.create(
            business_profile=self.bp, name="Acme", tax_id="A111"
        )
        self.client.login(username="owner", password="test")
        session = self.client.session
        session["active_business_id"] = self.bp.pk
        session.save()

    def test_export_invoices_csv(self):
        invoice = Invoice.objects.create(
            business_profile=self.bp,
            client=self.test_client,
            number="F-2026-00001",
            issue_date="2026-01-15",
        )
        InvoiceLineItem.objects.create(
            invoice=invoice,
            description="Service",
            quantity=Decimal("1"),
            unit_price=Decimal("1000"),
            tax_rate=Decimal("21"),
        )
        response = self.client.get("/exportar/facturas/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        content = response.content.decode("utf-8-sig")
        self.assertIn("F-2026-00001", content)
        self.assertIn("Acme", content)

    def test_export_invoices_csv_with_status_filter(self):
        Invoice.objects.create(
            business_profile=self.bp,
            client=self.test_client,
            number="F-2026-00001",
            issue_date="2026-01-15",
            status="draft",
        )
        Invoice.objects.create(
            business_profile=self.bp,
            client=self.test_client,
            number="F-2026-00002",
            issue_date="2026-01-16",
            status="sent",
        )
        response = self.client.get("/exportar/facturas/?status=sent")
        content = response.content.decode("utf-8-sig")
        self.assertIn("F-2026-00002", content)
        self.assertNotIn("F-2026-00001", content)

    def test_export_clients_csv(self):
        response = self.client.get("/exportar/clientes/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        content = response.content.decode("utf-8-sig")
        self.assertIn("Acme", content)
        self.assertIn("A111", content)

    def test_export_payments_csv(self):
        from apps.invoicing.models.payment import Payment

        invoice = Invoice.objects.create(
            business_profile=self.bp,
            client=self.test_client,
            number="F-2026-00001",
            issue_date="2026-01-15",
            status="sent",
        )
        Payment.objects.create(
            invoice=invoice,
            amount=Decimal("500"),
            date="2026-01-20",
            method="transfer",
        )
        response = self.client.get("/exportar/pagos/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8-sig")
        self.assertIn("F-2026-00001", content)
        self.assertIn("500", content)
