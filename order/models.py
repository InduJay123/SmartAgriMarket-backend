from django.db import models

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)

    buyer_id = models.IntegerField()
    market_id = models.IntegerField()

    quantity = models.PositiveIntegerField()

    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'  
        managed = False     

    def __str__(self):
        return f"Order {self.order_id}"
