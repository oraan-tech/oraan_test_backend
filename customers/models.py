from django.db import models


class Contact(models.Model):
    customer_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} ({self.customer_id})"


class Subscriptions(models.Model):
    OPT_SUB_STATUS_FUTURE = 'future'
    OPT_SUB_STATUS_LIVE = 'live'
    OPT_SUB_STATUS_EXPIRED = 'expired'

    STATUS_CHOICES = [
        (OPT_SUB_STATUS_FUTURE, 'Future'),
        (OPT_SUB_STATUS_LIVE, 'Live'),
        (OPT_SUB_STATUS_EXPIRED, 'Expired'),
    ]

    subscription_id = models.CharField(max_length=255, unique=True)
    customer_id = models.CharField(max_length=50)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    activated_at = models.DateField()
    expires_at = models.DateField()
    amount = models.FloatField()
    addon = models.FloatField(default=0)
    committee_specific_name = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Subscriptions"

    def __str__(self):
        return f"{self.subscription_id} - {self.status}"
