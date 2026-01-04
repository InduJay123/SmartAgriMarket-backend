from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Review
from .serializers import ReviewSerializer
from django.db.models import Avg, Count

@api_view(['GET'])
def get_reviews(request, product_id):
    reviews = Review.objects.filter(product_id=product_id)
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request):
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=200)
    print(serializer.errors)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def review_summary(request, market_id):
    summary = Review.objects.filter(
        product_id=market_id
    ).aggregate(
        avg=Avg('rating'),
        total=Count('id')
    )

    return Response({
        "avg": round(summary["avg"] or 0, 1),
        "total": summary["total"]
    })