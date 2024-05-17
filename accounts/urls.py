from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.list_accounts, name='list_accounts'),
    path('transaction/', views.transaction, name='transaction'),
    path('import_accounts/', views.import_accounts, name='import_accounts'),
    path('account_detail/<str:slug>/', views.account_detail, name='account_detail'),
    path('account_search/', views.account_search, name='account_search'),
]