"""
URL mappings for the transaction app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from transaction import views

# /transactions
router = DefaultRouter()
router.register('transactions', views.TransactionViewSet)
router.register('cc-merchant-categories', views.CreditCardMerchantCategoryViewSet)

app_name = 'transaction'

urlpatterns = [
    path('', include(router.urls)),
]
