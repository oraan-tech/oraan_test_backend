from django.db import models
from customers.models import Contact, Subscriptions


class ZohoInvoice(models.Model):
    STATUS_SENT = 'sent'
    STATUS_OVERDUE = 'overdue'
    STATUS_PAID = 'paid'

    STATUS_CHOICES = [
        (STATUS_SENT, 'Sent'),
        (STATUS_OVERDUE, 'Overdue'),
        (STATUS_PAID, 'Paid'),
    ]

    customer_id = models.CharField(max_length=50)
    subscription_id = models.CharField(max_length=255)
    subscription_id_fk = models.ForeignKey(Subscriptions, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    due_date = models.DateField()
    balance = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    committee_specific_name = models.CharField(max_length=255)
    fees = models.FloatField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Invoice {self.id} - {self.customer_id} - {self.status}"
