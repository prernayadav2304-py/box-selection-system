from django.contrib import admin
from django.urls import include, path

from boxes.views import DashboardView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", DashboardView.as_view(), name="dashboard"),
    path("api/", include("boxes.urls")),
]
