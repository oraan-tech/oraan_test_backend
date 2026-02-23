from django.urls import path
from invoices.views import GenerateInvoiceView

urlpatterns = [
    path('invoices/generate/', GenerateInvoiceView.as_view(), name='generate-invoice'),
]
