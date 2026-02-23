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
        customer_id = request.data.get('customer_id')

        if not customer_id:
            return Response(
                {'error': 'customer_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        print(f"Starting invoice generation for customer: {customer_id}")

        dateNow = datetime.today()
        current_date = datetime.strptime(str(dateNow), '%Y-%m-%d %H:%M:%S.%f').date()

        # Update subscription statuses from future to live
        print(f"Updating subscription statuses from future to live")
        subs_update_live = Subscriptions.objects.filter(
            Q(activated_at__lte=current_date) &
            Q(customer_id=customer_id) &
            Q(is_deleted=False) &
            Q(status='future')
        ).update(status='live')

        if subs_update_live > 0:
            print(f"Updated {subs_update_live} subscriptions to live status")
        else:
            print(f"No subscriptions updated to live status")

        # Update subscription statuses from live to expired
        print(f"Updating subscription statuses from live to expired")
        subs_update_expired = Subscriptions.objects.filter(
            Q(expires_at__lte=current_date) &
            Q(customer_id=customer_id) &
            Q(is_deleted=False) &
            Q(status='live')
        ).update(status='expired')

        if subs_update_expired > 0:
            print(f"Updated {subs_update_expired} subscriptions to expired status")
        else:
            print(f"No subscriptions updated to expired status")

        # Fetch live subscription data
        print(f"Fetching live subscription data for customer: {customer_id}")
        subscriptions_data = Subscriptions.objects.filter(
            customer_id=customer_id,
            status='live',
            is_deleted=False
        )

        if subscriptions_data.count() > 0:
            subscription = subscriptions_data.first()
            print(f"Found live subscription: {subscription.subscription_id}")

            current_year_month = datetime.strptime(str(dateNow), '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m')
            activation_year_month = datetime.strptime(str(subscription.activated_at), '%Y-%m-%d').strftime('%Y-%m')

            if str(activation_year_month) <= str(current_year_month):
                inv_count = self.get_months_difference(str(subscription.activated_at), current_date)
                print(f"Calculating invoices: {inv_count + 1} invoices needed")

                inv_date_arr = []

                contact = Contact.objects.filter(customer_id=subscription.customer_id).first()

                for i in range(0, inv_count + 1):
                    invoice_due_date = datetime.strptime(str(subscription.activated_at), '%Y-%m-%d') + \
                                     relativedelta.relativedelta(months=i)
                    invoice_due_date = datetime.strptime(str(invoice_due_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m') + "-11"
                    inv_date_arr.append(invoice_due_date)

                # Process each due date
                for due_date in inv_date_arr:
                    print(f"Processing invoice for due date: {due_date}")

                    invoice_data = ZohoInvoice.objects.filter(
                        subscription_id=subscription.subscription_id,
                        is_deleted=False,
                        due_date=due_date
                    )

                    if invoice_data.count() == 0:
                        print(f"No existing invoice found, creating new invoice")

                        if str(current_date) > str(due_date):
                            print(f"Creating overdue invoice (past due)")
                            ins_invoice = ZohoInvoice.objects.create(
                                customer_id=subscription.customer_id,
                                subscription_id=subscription.subscription_id,
                                due_date=due_date,
                                balance=subscription.amount,
                                status='overdue',
                                committee_specific_name=subscription.committee_specific_name,
                                fees=subscription.addon,
                                is_deleted=False,
                                created_at=dateNow,
                                contact=contact,
                                subscription_id_fk_id=subscription.id
                            )
                            if ins_invoice.pk is not None:
                                print(f"Overdue invoice created: {ins_invoice.pk}")
                            else:
                                print(f"Failed to create overdue invoice")

                        elif str(current_date) == str(due_date):
                            print(f"Creating overdue invoice (due today)")
                            ins_invoice = ZohoInvoice.objects.create(
                                customer_id=subscription.customer_id,
                                subscription_id=subscription.subscription_id,
                                due_date=due_date,
                                balance=subscription.amount,
                                status='overdue',
                                committee_specific_name=subscription.committee_specific_name,
                                fees=subscription.addon,
                                is_deleted=False,
                                created_at=dateNow,
                                contact=contact,
                                subscription_id_fk_id=subscription.id
                            )
                            if ins_invoice.pk is not None:
                                print(f"Overdue invoice created: {ins_invoice.pk}")
                            else:
                                print(f"Failed to create overdue invoice")

                        elif str(current_date) < str(due_date):
                            print(f"Creating sent invoice (future due)")
                            ins_invoice = ZohoInvoice.objects.create(
                                customer_id=subscription.customer_id,
                                subscription_id=subscription.subscription_id,
                                due_date=due_date,
                                balance=subscription.amount,
                                status='sent',
                                committee_specific_name=subscription.committee_specific_name,
                                fees=subscription.addon,
                                is_deleted=False,
                                created_at=dateNow,
                                contact=contact,
                                subscription_id_fk_id=subscription.id
                            )
                            if ins_invoice.pk is not None:
                                print(f"Sent invoice created: {ins_invoice.pk}")
                            else:
                                print(f"Failed to create sent invoice")
                    else:
                        print(f"Invoice already exists for due date: {due_date}")

            return Response({
                'message': 'Invoice generation completed',
                'customer_id': customer_id
            }, status=status.HTTP_200_OK)
        else:
            print(f"No live subscription data found for customer: {customer_id}")
            return Response({
                'message': 'No live subscriptions found',
                'customer_id': customer_id
            }, status=status.HTTP_200_OK)
