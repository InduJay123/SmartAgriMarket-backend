from django.db.models import Avg, Count, Sum
from apps.products.models import Price
from apps.accounts.models import User
from apps.orders.models import Order

class ReportsService:

    @staticmethod
    def price_trends():
        return (
            Price.objects
            .values('crop__name', 'date__month')
            .annotate(avg_price=Avg('price'))
            .order_by('date__month')
        )

    @staticmethod
    def farmers_activity():
        return {
            "total_farmers": User.objects.filter(role='FARMER').count(),
            "verified": User.objects.filter(role='FARMER', is_verified=True).count(),
            "pending": User.objects.filter(role='FARMER', is_verified=False).count(),
        }

    @staticmethod
    def market_transactions():
        return (
            Order.objects
            .values('status')
            .annotate(
                total_orders=Count('id'),
                total_value=Sum('total_price')
            )
        )
