from django.shortcuts import render


from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.accounts.models import User
from apps.products.models import Product

@api_view(['GET'])
def admin_stats(request):
    return Response({
        "verified_farmers": User.objects.filter(role='FARMER', is_verified=True).count(),
        "pending_approvals": User.objects.filter(is_verified=False).count(),
        # "buyers": User.objects.filter(role='BUYER').count(),
        # "crops": Product.objects.count(),
    })

