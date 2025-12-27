from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer

# Create your views here.
@api_view(['POST'])
def place_order(request):
    data = request.data

    required_fields = [
        'buyer_id','market_id','quantity','price_at_order','total_amount',
        'full_name','phone','address','city'
    ]

    for field in required_fields:
        if field not in data:
            return Response(
                {"error": f"{field} is required"},
                status = status.HTTP_400_BAD_REQUEST
            )

    order=Order.objects.create(
        buyer_id=data['buyer_id'],
        market_id=data['market_id'],
        quantity=data['quantity'],
        price_at_order=data['price_at_order'],
        total_amount=data['total_amount'],
        full_name=data['full_name'],
        phone=data['phone'],
        address=data['address'],
        city=data['city']
    )

    serializer = OrderSerializer(order)

    return Response(
        {
            "message": "Order placed succefully",
            "order": serializer.data
        },
        status=status.HTTP_201_CREATED
    )

@api_view(['GET'])
def buyer_orders(request, buyer_id):
    from django.db import connection

    query = """
        SELECT
            o.order_id,
            o.buyer_id,
            o.market_id,
            o.quantity,
            o.price_at_order,
            o.total_amount,
            o.status,
            o.full_name,
            o.phone,
            o.address,
            o.city,
            o.created_at,

            m.image AS product_image,
            u.fullname AS farmer_name,
            c.crop_name AS product_name
        FROM orders o
        JOIN market m ON o.market_id = m.market_id
        JOIN users u ON m.farmer_id = u.user_id
        JOIN crops c ON m.crop_id = c.crop_id
        WHERE o.buyer_id = %s
        ORDER BY o.created_at DESC
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [buyer_id])
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    data = [dict(zip(columns, row)) for row in rows]
    return Response(data)

@api_view(['GET'])
def farmer_orders(request, farmer_id):
    from django.db import connection

    query = """
        SELECT
            o.order_id,
            o.buyer_id,
            o.market_id,
            o.quantity,
            o.price_at_order,
            o.total_amount,
            o.status,
            o.full_name,
            o.phone,
            o.address,
            o.city,
            o.created_at,

            c.crop_name AS product_name,
            m.image AS product_image
        FROM orders o
        JOIN market m ON o.market_id = m.market_id
        JOIN crops c ON m.crop_id = c.crop_id
        WHERE m.farmer_id = %s
        ORDER BY o.created_at DESC
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [farmer_id])
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    data = [dict(zip(columns, row)) for row in rows]
    return Response(data, status=status.HTTP_200_OK)