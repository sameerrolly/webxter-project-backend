"""
URL patterns for the orders app.
Mounted at: /api/v1/orders/
"""

from django.urls import path
from .views import OrderListCreateView, OrderDetailView

app_name = "orders"

urlpatterns = [
    path("", OrderListCreateView.as_view(), name="order_list_create"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
]
