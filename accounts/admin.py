from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Account, Transaction

# Register your models here.

class AccountAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['name', 'balance']
    search_fields = ['name']
    list_per_page = 50


class TransactionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'amount', 'date']
    search_fields = ['sender__name', 'receiver__name']
    list_per_page = 50


admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
