from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from customers.models import Contact, Subscriptions
from invoices.models import ZohoInvoice
from django.utils.timezone import datetime
from dateutil import relativedelta
from django.db.models import Q


class GenerateInvoiceView(APIView):
    """
    API endpoint to generate invoices for active subscriptions.

    WARNING: This code has intentional bugs and architectural issues
    """

    def get_months_difference(self, activated_at, current_date):
        """Calculate months between activation date and current date."""
        activated_at = datetime.strptime(activated_at, '%Y-%m-%d').date()
        current_date = datetime.strptime(str(current_date), '%Y-%m-%d').date()
        diff = relativedelta.relativedelta(current_date, activated_at)
        return diff.months

    def post(self, request):
        print(f"Starting invoice generation for all customers")

        dateNow = datetime.today()
        current_date = datetime.strptime(str(dateNow), '%Y-%m-%d %H:%M:%S.%f').date()
        formatted_date = current_date.strftime('%Y-%m-%d')

        # Update subscription statuses from future to live
        print(f"Updating subscription statuses from future to live")
        subs_update_live = Subscriptions.objects.filter(
            is_deleted=False,
            status=Subscriptions.OPT_SUB_STATUS_FUTURE,
            activated_at__lte=formatted_date
        ).update(status=Subscriptions.OPT_SUB_STATUS_LIVE)

        if subs_update_live > 0:
            print(f"Updated {subs_update_live} subscriptions to live status")
        else:
            print(f"No subscriptions updated to live status")

        # Update subscription statuses from live to expired
        print(f"Updating subscription statuses from live to expired")
        subs_update_expired = Subscriptions.objects.filter(
            is_deleted=False,
            status=Subscriptions.OPT_SUB_STATUS_LIVE,
            expires_at__lte=formatted_date
        ).update(status=Subscriptions.OPT_SUB_STATUS_EXPIRED)

        if subs_update_expired > 0:
            print(f"Updated {subs_update_expired} subscriptions to expired status")
        else:
            print(f"No subscriptions updated to expired status")

        # Fetch ALL live subscriptions (not just for one customer)
        print(f"Fetching all live subscriptions")
        subscriptions_data = Subscriptions.objects.filter(
            is_deleted=False,
            status=Subscriptions.OPT_SUB_STATUS_LIVE
        )

        invoices_created_count = 0
        print(f"Found {subscriptions_data.count()} live subscriptions to process")

        # Process each subscription
        for subscription in subscriptions_data:
            print(f"Processing subscription: {subscription.subscription_id} for customer: {subscription.customer_id}")

            current_year_month = datetime.strptime(str(dateNow), '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m')
            activation_year_month = datetime.strptime(str(subscription.activated_at), '%Y-%m-%d').strftime('%Y-%m')

            if str(activation_year_month) <= str(current_year_month):
                # BUG #1: N+1 Query - Contact fetched inside loop for each subscription
                contact = Contact.objects.filter(customer_id=subscription.customer_id).first()

                # Check if invoice already exists for current month
                check_invoice = ZohoInvoice.objects.filter(
                    is_deleted=False,
                    subscription_id=subscription.subscription_id,
                    due_date__startswith=current_year_month
                ).exists()

                if not check_invoice:
                    invoice_due_date = current_year_month + "-11"
                    print(f"Creating new invoice for due date: {invoice_due_date}")

                    # Create the invoice
                    created_invoice = ZohoInvoice.objects.create(
                        customer_id=subscription.customer_id,
                        subscription_id=subscription.subscription_id,
                        due_date=invoice_due_date,
                        balance=subscription.amount,
                        status='sent',
                        committee_specific_name=subscription.committee_specific_name,
                        fees=subscription.addon,
                        is_deleted=False,
                        contact=contact,
                        subscription_id_fk_id=subscription.id
                    )

                    invoices_created_count += 1
                    print(f"Invoice created: {created_invoice.pk} for subscription: {subscription.subscription_id}")
                else:
                    print(f"Invoice already exists for current month for subscription: {subscription.subscription_id}")
            else:
                print(f"Subscription {subscription.subscription_id} not yet activated for current month")

        print(f"Invoice generation completed. Created {invoices_created_count} invoices.")
        return Response({
            'message': 'Invoice generation completed',
            'invoices_created': invoices_created_count
        }, status=status.HTTP_200_OK)
