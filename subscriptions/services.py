import hashlib
import time
from urllib.parse import urlencode
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def minimal_robokassa_test(request):
    """
    Максимально упрощенный тест Робокассы без дополнительных параметров
    """
    try:
        # Базовые параметры (минимально необходимые)
        merchant_login = "Psgamezz"  # Hardcoded для теста
        test_password = "G6aPODIgpupDIL9y3Qq9"  # Тестовый пароль #1

        # Числовой ID заказа
        inv_id = str(int(time.time()))
        # Сумма заказа (2 знака после запятой)
        out_sum = "10.00"

        # Формирование подписи (без доп. параметров)
        signature_string = f"{merchant_login}:{out_sum}:{inv_id}:{test_password}"
        signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()

        # Базовые параметры для URL
        params = {
            'MerchantLogin': merchant_login,
            'OutSum': out_sum,
            'InvId': inv_id,
            'Description': "Тестовый платеж",
            'SignatureValue': signature,
            'IsTest': 1,
            'Culture': 'ru'
        }

        # Формирование URL
        base_url = 'https://auth.robokassa.ru/Merchant/Index.aspx'
        payment_url = f"{base_url}?{urlencode(params)}"

        return Response({
            'test_url': payment_url,
            'params': params,
            'signature_string': signature_string
        })

    except Exception as e:
        return Response({'error': str(e)}, status=500)