from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import ConsoleType, SubscriptionService, Subscription
from .serializers import (ConsoleTypeSerializer, SubscriptionServiceSerializer,
                          SubscriptionSerializer)


class ConsoleTypeViewSet(viewsets.ModelViewSet):
    queryset = ConsoleType.objects.all()
    serializer_class = ConsoleTypeSerializer
    permission_classes = [IsAdminUser]


class SubscriptionServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubscriptionService.objects.all()
    serializer_class = SubscriptionServiceSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
