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
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .services import RobokassaService
from .models import SubscriptionService, SubscriptionPeriod, ConsoleType, Payment
from django.contrib.auth.models import User
import logging
import time
import hashlib
from urllib.parse import urlencode
from django.conf import settings

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    logger.info(f"=== НАЧАЛО ИНИЦИАЦИИ ПЛАТЕЖА ===")
    logger.info(f"User: {request.user.username} (ID: {request.user.id})")
    logger.info(f"Request data: {request.data}")

    try:
        subscription_service_id = request.data.get('subscription_service_id')
        subscription_period_id = request.data.get('subscription_period_id')
        console_type_id = request.data.get('console_type_id')

        logger.info(
            f"Params: service={subscription_service_id}, period={subscription_period_id}, console={console_type_id}")

        if not all([subscription_service_id, subscription_period_id, console_type_id]):
            logger.error("Missing required parameters")
            return Response({'error': 'Не все обязательные параметры указаны'}, status=400)

        subscription_service = get_object_or_404(SubscriptionService, id=subscription_service_id)
        subscription_period = get_object_or_404(SubscriptionPeriod, id=subscription_period_id)
        console_type = get_object_or_404(ConsoleType, id=console_type_id)

        logger.info(f"Found service: {subscription_service}")
        logger.info(f"Found period: {subscription_period}")
        logger.info(f"Found console: {console_type}")

        payment = RobokassaService.create_payment(
            user=request.user,
            subscription_service=subscription_service,
            subscription_period=subscription_period,
            console_type=console_type
        )

        logger.info(f"Created payment: ID={payment.id}, invoice={payment.invoice_id}, amount={payment.amount}")

        payment_url = RobokassaService.get_payment_url(payment)
        logger.info(f"Generated payment URL, length: {len(payment_url)}")

        response_data = {'payment_url': payment_url, 'invoice_id': payment.invoice_id}
        logger.info(f"Returning response: {response_data}")
        logger.info(f"=== КОНЕЦ ИНИЦИАЦИИ ПЛАТЕЖА ===")
        return Response(response_data)

    except Exception as e:
        logger.error(f"Error during payment initiation: {str(e)}")
        logger.exception(e)  # Подробная информация об ошибке со стеком вызовов
        logger.info(f"=== ОШИБКА ИНИЦИАЦИИ ПЛАТЕЖА ===")
        return Response({'error': str(e)}, status=500)


@csrf_exempt
def payment_result(request):
    logger.info(f"=== ПОЛУЧЕНО УВЕДОМЛЕНИЕ ОТ РОБОКАССЫ ===")

    # Получаем данные в зависимости от метода запроса
    if request.method == 'POST':
        data = request.POST.dict()
    else:  # GET
        data = request.GET.dict()

    logger.info(f"Request method: {request.method}")
    logger.info(f"Request data: {data}")

    if not RobokassaService.check_signature(data):
        logger.error("Invalid signature from Robokassa")
        return HttpResponse("Неверная подпись", status=400)

    success, message = RobokassaService.process_payment(data)

    if success:
        logger.info("Payment processed successfully")
        logger.info(f"=== КОНЕЦ ОБРАБОТКИ УВЕДОМЛЕНИЯ ===")
        return HttpResponse("OK")
    else:
        logger.error(f"Payment processing failed: {message}")
        logger.info(f"=== ОШИБКА ОБРАБОТКИ УВЕДОМЛЕНИЯ ===")
        return HttpResponse(message, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def payment_success(request):
    logger.info(f"=== СТРАНИЦА УСПЕШНОЙ ОПЛАТЫ ===")
    logger.info(f"Request params: {request.GET}")
    inv_id = request.GET.get('InvId')
    logger.info(f"Invoice ID: {inv_id}")

    try:
        payment = get_object_or_404(Payment, invoice_id=inv_id)
        logger.info(f"Found payment: {payment}")
        logger.info(f"Payment status: {payment.status}")

        if payment.status != 'success':
            logger.info("Payment is pending, waiting for status update")
            return Response({
                'status': 'pending',
                'message': 'Платеж обрабатывается. Пожалуйста, подождите.'
            })

        logger.info("Returning success response")
        logger.info(f"=== КОНЕЦ СТРАНИЦЫ УСПЕШНОЙ ОПЛАТЫ ===")
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
        logger.error(f"Payment with ID {inv_id} not found")
        logger.info(f"=== ОШИБКА СТРАНИЦЫ УСПЕШНОЙ ОПЛАТЫ ===")
        return Response({'error': 'Платеж не найден'}, status=404)
    except Exception as e:
        logger.error(f"Error processing success page: {str(e)}")
        logger.exception(e)
        logger.info(f"=== ОШИБКА СТРАНИЦЫ УСПЕШНОЙ ОПЛАТЫ ===")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def payment_fail(request):
    logger.info(f"=== СТРАНИЦА НЕУДАЧНОЙ ОПЛАТЫ ===")
    logger.info(f"Request params: {request.GET}")
    inv_id = request.GET.get('InvId')
    logger.info(f"Invoice ID: {inv_id}")

    try:
        payment = get_object_or_404(Payment, invoice_id=inv_id)
        logger.info(f"Found payment: {payment}")

        if payment.status != 'failed':
            logger.info(f"Updating payment status to failed")
            payment.status = 'failed'
            payment.save()

        logger.info("Returning failed payment response")
        logger.info(f"=== КОНЕЦ СТРАНИЦЫ НЕУДАЧНОЙ ОПЛАТЫ ===")
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
        logger.error(f"Payment with ID {inv_id} not found")
        logger.info(f"=== ОШИБКА СТРАНИЦЫ НЕУДАЧНОЙ ОПЛАТЫ ===")
        return Response({'error': 'Платеж не найден'}, status=404)
    except Exception as e:
        logger.error(f"Error processing fail page: {str(e)}")
        logger.exception(e)
        logger.info(f"=== ОШИБКА СТРАНИЦЫ НЕУДАЧНОЙ ОПЛАТЫ ===")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_payments(request):
    logger.info(f"=== ПОЛУЧЕНИЕ ИСТОРИИ ПЛАТЕЖЕЙ ===")
    logger.info(f"User: {request.user.username} (ID: {request.user.id})")

    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    logger.info(f"Found {payments.count()} payments")

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

    logger.info(f"=== КОНЕЦ ПОЛУЧЕНИЯ ИСТОРИИ ПЛАТЕЖЕЙ ===")
    return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def test_robokassa(request):
    """
    Тестовый эндпоинт для проверки Робокассы с минимальными параметрами
    """
    logger.info("=== ТЕСТОВЫЙ ЗАПРОС К РОБОКАССЕ ===")

    try:
        # Базовые параметры
        merchant_login = settings.ROBOKASSA_MERCHANT_LOGIN
        password = settings.ROBOKASSA_TEST_PASSWORD1 if settings.ROBOKASSA_TEST_MODE else settings.ROBOKASSA_PASSWORD1

        # Минимальные тестовые параметры
        invoice_id = f"test{int(time.time())}"
        amount = "10.00"
        description = "Тестовый платеж"

        logger.info(f"MerchantLogin: {merchant_login}")
        logger.info(f"OutSum: {amount}")
        logger.info(f"InvId: {invoice_id}")

        # Простая подпись без Shp_ параметров
        signature_value = f"{merchant_login}:{amount}:{invoice_id}:{password}"
        logger.info(f"Signature string: {signature_value}")

        signature = hashlib.md5(signature_value.encode()).hexdigest()
        logger.info(f"MD5 hash: {signature}")

        # Минимальный набор параметров
        params = {
            'MerchantLogin': merchant_login,
            'OutSum': amount,
            'InvId': invoice_id,
            'Description': description,
            'SignatureValue': signature,
            'IsTest': 1,
            'Culture': 'ru',
        }

        logger.info(f"All params: {params}")

        # Формирование URL
        base_url = 'https://auth.robokassa.ru/Merchant/Index.aspx'
        final_url = f"{base_url}?{urlencode(params)}"

        logger.info(f"Final URL: {final_url}")
        logger.info("=== КОНЕЦ ТЕСТОВОГО ЗАПРОСА ===")

        return Response({
            'test_url': final_url,
            'params': params
        })
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        logger.exception(e)
        return Response({'error': str(e)}, status=500)


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