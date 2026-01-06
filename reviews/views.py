from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
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
    if not hasattr(request.user, "buyerdetails"):
        return Response(
            {"error": "Only buyers can add reviews"},
            status=403
        )

    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=200)
    print(serializer.errors)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
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

@api_view(['GET'])
def farmer_rating_summary(request, farmer_id):
    summary = Review.objects.filter(
        product__farmer_id=farmer_id
    ).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )

    avg = summary["avg_rating"] or 0

    return Response({
        "farmer_id": farmer_id,
        "average_rating": round(avg, 1),   # max 5.0
        "total_reviews": summary["total_reviews"],
        "max_rating": 5
    })