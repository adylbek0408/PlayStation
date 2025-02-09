from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConsoleTypeViewSet, SubscriptionServiceViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register(r'console-types', ConsoleTypeViewSet)
router.register(r'subscription-services', SubscriptionServiceViewSet)
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
]
