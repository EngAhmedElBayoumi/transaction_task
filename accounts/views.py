from django.shortcuts import render , redirect
from .models import Account , Transaction
from django.db import transaction as transactiondb
import csv
from django.core.paginator import Paginator
from django.contrib import messages
from decimal import Decimal

# Create your views here.
def validate_file(file):
    if not file.name.endswith('.csv'):
        context={'error': 'Invalid file type'}
        return context
    if file.size == 0:
        context={'error': 'Empty file'}
        return context
    
    context={'error': None}
    return context


def import_accounts(request):
    if request.method == 'POST':
        try:
            file = request.FILES['csv_file']
        except:
            messages.error(request, 'No file uploaded')
            return render(request, 'import_accounts.html')
        context = validate_file(file)
        if context['error']:
            messages.error(request, context['error'])
            return render(request, 'import_accounts.html')
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        for row in reader:
            if row[0] == 'ID':
                continue
            try:
                account = Account(
                    id=row[0],
                    name=row[1],
                    balance=row[2]
                )
                account.save()
            except Exception as e:
                #skip the row if there is an error and create message with this error and row number
                messages.error(request, f'Error importing row {reader.line_num} => {row} with error {e}')
                continue
        messages.success(request, 'Accounts imported successfully')
    return render(request, 'import_accounts.html')


def list_accounts(request):
    accounts = Account.objects.all()
    paginator = Paginator(accounts, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_accounts = accounts.count()
    total_balance = sum([account.balance for account in accounts])
    context = {
        'accounts': page_obj,
        'total_accounts': total_accounts,
        'total_balance': total_balance,
    }
    return render(request, 'list_accounts.html', context)


def account_detail(request, slug):
    account = Account.objects.get(slug=slug)
    transactions_send = Transaction.objects.filter(sender=account).select_related('receiver')
    transactions_receive = Transaction.objects.filter(receiver=account).select_related('sender')
    context={'account': account, 'send': transactions_send, 'receive': transactions_receive}
    return render(request, 'account_detail.html', context)


def transaction(request):
    accounts = Account.objects.all()
    context = {'accounts': accounts}

    if request.method == 'POST':
        sender_id = request.POST['sender']
        receiver_id = request.POST['receiver']
        amount = request.POST['amount']

        if not sender_id or not receiver_id or not amount or amount <= '0':
            messages.error(request, 'All fields are required')
            return redirect('accounts:transaction')

        if sender_id == receiver_id:
            messages.error(request, 'You cannot send money to yourself')
            return redirect('accounts:transaction')

        try:
            amount = Decimal(amount)
        except:
            messages.error(request, 'Invalid amount')
            return redirect('accounts:transaction')

        try:
            with transactiondb.atomic():
                # Lock the sender and receiver accounts
                sender = Account.objects.select_for_update().get(id=sender_id)
                receiver = Account.objects.select_for_update().get(id=receiver_id)

                if sender.balance < amount:
                    messages.error(request, 'This account has insufficient funds')
                    return redirect('accounts:transaction')

                # Perform the transaction
                sender.balance -= amount
                receiver.balance += amount

                sender.save()
                receiver.save()

                # Create the transaction record
                new_transaction = Transaction(
                    sender=sender,
                    receiver=receiver,
                    amount=amount,
                )
                new_transaction.save()

                messages.success(request, 'Transaction successful')

        except Account.DoesNotExist:
            messages.error(request, 'Account not found')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    return render(request, 'transaction.html', context)


def account_search(request):
    query = request.GET.get('search')
    accounts = Account.objects.filter(name__icontains=query)
    paginator = Paginator(accounts, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_accounts = accounts.count()
    total_balance = sum([account.balance for account in accounts])
    context = {
        'accounts': page_obj,
        'total_accounts': total_accounts,
        'total_balance': total_balance,
    }
    return render(request, 'list_accounts.html', context)


def error_404(request, exception):
    messages.error(request, 'Page not found')
    return redirect('accounts:list_accounts')


def error_500(request):
    messages.error(request, 'Unknown server error')
    return redirect('accounts:list_accounts')