from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import ConsoleType, SubscriptionService, Subscription
from .serializers import (ConsoleTypeSerializer, SubscriptionServiceSerializer,
                          SubscriptionSerializer)
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services import RobokassaService
from .models import SubscriptionService, SubscriptionPeriod, ConsoleType, Payment


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    try:
        subscription_service_id = request.data.get('subscription_service_id')
        subscription_period_id = request.data.get('subscription_period_id')
        console_type_id = request.data.get('console_type_id')
        if not all([subscription_service_id, subscription_period_id, console_type_id]):
            return Response({'error': 'Не все обязательные параметры указаны'}, status=400)
        subscription_service = get_object_or_404(SubscriptionService, id=subscription_service_id)
        subscription_period = get_object_or_404(SubscriptionPeriod, id=subscription_period_id)
        console_type = get_object_or_404(ConsoleType, id=console_type_id)
        payment = RobokassaService.create_payment(
            user=request.user,
            subscription_service=subscription_service,
            subscription_period=subscription_period,
            console_type=console_type
        )
        payment_url = RobokassaService.get_payment_url(payment)
        return Response({'payment_url': payment_url, 'invoice_id': payment.invoice_id})

    except Exception as e:
        return Response({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def payment_result(request):
    data = request.POST.dict()
    if not RobokassaService.check_signature(data):
        return HttpResponse("Неверная подпись", status=400)
    success, message = RobokassaService.process_payment(data)
    if success:
        return HttpResponse("OK")
    else:
        return HttpResponse(message, status=400)


@api_view(['GET'])
def payment_success(request):
    inv_id = request.GET.get('InvId')

    try:
        payment = get_object_or_404(Payment, invoice_id=inv_id)
        if payment.status != 'success':
            return Response({
                'status': 'pending',
                'message': 'Платеж обрабатывается. Пожалуйста, подождите.'
            })
        return Response({
            'status': 'success',
            'message': 'Платеж успешно завершен',
            'subscription': {
                'service': payment.subscription_service.name,
                'level': payment.subscription_service.choices_level,
                'period': f"{payment.subscription_period.months} месяцев",
                'price': str(payment.amount)
            }
        })

    except Payment.DoesNotExist:
        return Response({'error': 'Платеж не найден'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def payment_fail(request):
    inv_id = request.GET.get('InvId')

    try:
        payment = get_object_or_404(Payment, invoice_id=inv_id)
        if payment.status != 'failed':
            payment.status = 'failed'
            payment.save()

        return Response({
            'status': 'failed',
            'message': 'Оплата не была произведена',
            'subscription': {
                'service': payment.subscription_service.name,
                'level': payment.subscription_service.choices_level,
                'period': f"{payment.subscription_period.months} месяцев",
                'price': str(payment.amount)
            }
        })

    except Payment.DoesNotExist:
        return Response({'error': 'Платеж не найден'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_payments(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    result = []
    for payment in payments:
        result.append({
            'id': payment.id,
            'invoice_id': payment.invoice_id,
            'amount': str(payment.amount),
            'description': payment.description,
            'status': payment.status,
            'created_at': payment.created_at.isoformat(),
            'subscription': {
                'service': payment.subscription_service.name,
                'level': payment.subscription_service.choices_level,
                'period': f"{payment.subscription_period.months} месяцев",
            }
        })

    return Response(result)


class ConsoleTypeViewSet(viewsets.ReadOnlyModelViewSet):
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
