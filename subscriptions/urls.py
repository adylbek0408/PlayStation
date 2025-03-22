from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .auth import CustomAuthToken
from .views import (
    ConsoleTypeViewSet, SubscriptionServiceViewSet, SubscriptionViewSet,
    initiate_payment, payment_result, payment_success, payment_fail, user_payments,
    test_robokassa, minimal_robokassa_test  # Импортируем новую функцию
)

router = DefaultRouter()
router.register(r'console-types', ConsoleTypeViewSet)
router.register(r'subscription-services', SubscriptionServiceViewSet)
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),

    path('token/', CustomAuthToken.as_view(), name='api_token_auth'),

    path('payment/initiate/', initiate_payment, name='initiate_payment'),
    path('payment/result/', payment_result, name='payment_result'),
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/fail/', payment_fail, name='payment_fail'),
    path('payment/history/', user_payments, name='user_payments'),
    path('payment/test-robokassa/', test_robokassa, name='test_robokassa'),
    path('payment/minimal-robokassa-test/', minimal_robokassa_test, name='minimal_robokassa_test'),  # Новый маршрут
]