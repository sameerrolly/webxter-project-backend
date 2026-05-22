"""
Order CRUD — users can only access their own orders.
"""

from rest_framework import generics, permissions
from .models import Order
from .serializers import OrderSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/orders/   — list authenticated user's orders
    POST /api/v1/orders/   — create a new order
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user).select_related("project")

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/orders/<id>/  — retrieve an order
    PATCH  /api/v1/orders/<id>/  — partial update
    DELETE /api/v1/orders/<id>/  — delete
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user)
