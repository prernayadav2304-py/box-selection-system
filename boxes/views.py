from django.db.models import ProtectedError
from django.views.generic import TemplateView
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, Product, ShippingBox
from .serializers import (OrderSerializer, ProductSerializer, RecommendRequestSerializer,
                          ShippingBoxSerializer)
from .services import run_recommendation


class DashboardView(TemplateView):
    template_name = "dashboard.html"


class ProtectedDeleteMixin:
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response({"detail": "Cannot delete: used by existing orders."},
                            status=status.HTTP_409_CONFLICT)


class ProductViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ShippingBoxViewSet(viewsets.ModelViewSet):
    queryset = ShippingBox.objects.all()
    serializer_class = ShippingBoxSerializer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.select_related("box").prefetch_related("items__product")
    serializer_class = OrderSerializer


class RecommendView(APIView):
    def post(self, request):
        ser = RecommendRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = run_recommendation(ser.validated_data["items"])
        return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})
