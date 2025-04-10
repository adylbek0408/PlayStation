from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.views.decorators.csrf import csrf_exempt
from subscriptions.views import payment_success, payment_fail

schema_view = get_schema_view(
    openapi.Info(
        title="PlayStation API",
        default_version='v1',
        description="API documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('subscriptions.urls')),

    path('payment/success/', csrf_exempt(payment_success), name='direct_payment_success'),
    path('payment/fail/', csrf_exempt(payment_fail), name='direct_payment_fail'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
]