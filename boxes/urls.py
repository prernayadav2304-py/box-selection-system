from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, ProductViewSet, RecommendView, ShippingBoxViewSet, health

router = DefaultRouter()
router.register("products", ProductViewSet)
router.register("boxes", ShippingBoxViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [
    path("recommend/", RecommendView.as_view(), name="recommend"),
    path("health/", health, name="health"),
    path("", include(router.urls)),
]
