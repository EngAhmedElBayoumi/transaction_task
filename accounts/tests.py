from django.test import TestCase, Client
from django.urls import reverse
from .models import Account, Transaction
import uuid
from decimal import Decimal

class AccountModelTest(TestCase):
    def setUp(self):
        self.account = Account.objects.create(
            id=uuid.uuid4(),
            name="Test Account",
            balance=Decimal("100.00")
        )

    def test_account_creation(self):
        self.assertEqual(self.account.name, "Test Account")
        self.assertEqual(self.account.balance, Decimal("100.00"))
        self.assertTrue(self.account.slug)

    def test_account_slug_uniqueness(self):
        duplicate_account = Account(
            id=uuid.uuid4(),
            name=self.account.name,
            balance=Decimal("200.00")
        )
        duplicate_account.save()
        self.assertNotEqual(self.account.slug, duplicate_account.slug)

class TransactionModelTest(TestCase):
    def setUp(self):
        self.sender = Account.objects.create(
            id=uuid.uuid4(),
            name="Sender Account",
            balance=Decimal("200.00")
        )
        self.receiver = Account.objects.create(
            id=uuid.uuid4(),
            name="Receiver Account",
            balance=Decimal("100.00")
        )
        self.transaction = Transaction.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            amount=Decimal("50.00")
        )

    def test_transaction_creation(self):
        self.assertEqual(self.transaction.sender, self.sender)
        self.assertEqual(self.transaction.receiver, self.receiver)
        self.assertEqual(self.transaction.amount, Decimal("50.00"))

class AccountViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.account = Account.objects.create(
            id=uuid.uuid4(),
            name="Test Account",
            balance=Decimal("100.00")
        )

    def test_list_accounts_view(self):
        response = self.client.get(reverse('accounts:list_accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Account")

    def test_account_detail_view(self):
        response = self.client.get(reverse('accounts:account_detail', args=[self.account.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Account")

class TransactionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender = Account.objects.create(
            id=uuid.uuid4(),
            name="Sender Account",
            balance=Decimal("200.00")
        )
        self.receiver = Account.objects.create(
            id=uuid.uuid4(),
            name="Receiver Account",
            balance=Decimal("100.00")
        )

    def test_transaction_view(self):
        response = self.client.post(reverse('accounts:transaction'), {
            'sender': self.sender.id,
            'receiver': self.receiver.id,
            'amount': '50.00'
        })
        self.assertEqual(response.status_code, 302)
        self.sender.refresh_from_db()
        self.receiver.refresh_from_db()
        self.assertEqual(self.sender.balance, Decimal("150.00"))
        self.assertEqual(self.receiver.balance, Decimal("150.00"))
