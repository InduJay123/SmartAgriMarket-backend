from django.contrib import admin
from .models import Order, OrderItem, Transaction

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('unit_price','subtotal')
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','buyer','status','created_at','total_amount')
    inlines = [OrderItemInline]
    list_filter = ('status','created_at')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id','order','amount','status','created_at')
    search_fields = ('provider_txn_id',)
