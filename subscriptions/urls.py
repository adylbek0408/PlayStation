from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.decorators.csrf import csrf_exempt

from .auth import CustomAuthToken
from .views import (
    ConsoleTypeViewSet, SubscriptionServiceViewSet, SubscriptionViewSet,
    initiate_payment, payment_result, payment_success, payment_fail,
    user_payments, test_robokassa, compare_logins_test,
    test_minimal_connection, test_payment_with_both_logins
)

router = DefaultRouter()
router.register(r'console-types', ConsoleTypeViewSet)
router.register(r'subscription-services', SubscriptionServiceViewSet)
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),

    path('token/', CustomAuthToken.as_view(), name='api_token_auth'),

    path('payment/initiate/', initiate_payment, name='initiate_payment'),
    path('payment/result/', csrf_exempt(payment_result), name='payment_result'),
    path('payment/success/', csrf_exempt(payment_success), name='payment_success'),
    path('payment/fail/', csrf_exempt(payment_fail), name='payment_fail'),
    path('payment/history/', user_payments, name='user_payments'),

    path('payment/test-robokassa/', test_robokassa, name='test_robokassa'),
    path('payment/compare-logins/', compare_logins_test, name='compare_logins_test'),
    path('payment/test-connection/', test_minimal_connection, name='test_minimal_connection'),
    path('payment/test-both-logins/', test_payment_with_both_logins, name='test_payment_with_both_logins'),
]