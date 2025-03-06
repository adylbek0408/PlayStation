import hashlib
import uuid
from urllib.parse import urlencode
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import Payment, Subscription


class RobokassaService:
    @staticmethod
    def generate_invoice_id():
        return str(uuid.uuid4().hex)[:20]

    @staticmethod
    def get_payment_url(payment):
        merchant_login = settings.ROBOKASSA_MERCHANT_LOGIN
        password = settings.ROBOKASSA_TEST_PASSWORD1 if settings.ROBOKASSA_TEST_MODE else settings.ROBOKASSA_PASSWORD1

        invoice_id = payment.invoice_id
        amount = payment.amount
        description = payment.description

        signature_value = f"{merchant_login}:{amount}:{invoice_id}:{password}"

        shp_params = {
            'Shp_user_id': payment.user.id,
            'Shp_subscription_service': payment.subscription_service.id,
            'Shp_subscription_period': payment.subscription_period.id,
            'Shp_console_type': payment.console_type.id,
        }

        sorted_shp_params = sorted(shp_params.items())
        for key, value in sorted_shp_params:
            signature_value += f":{key}={value}"
        signature = hashlib.md5(signature_value.encode()).hexdigest()
        params = {
            'MerchantLogin': merchant_login,
            'OutSum': amount,
            'InvId': invoice_id,
            'Description': description,
            'SignatureValue': signature,
            'IsTest': 1 if settings.ROBOKASSA_TEST_MODE else 0,
            'Culture': 'ru',
        }
        params.update(shp_params)

        base_url = 'https://auth.robokassa.ru/Merchant/Index.aspx'

        return f"{base_url}?{urlencode(params)}"

    @staticmethod
    def check_signature(request_data):
        if settings.ROBOKASSA_TEST_MODE:
            password = settings.ROBOKASSA_TEST_PASSWORD2
        else:
            password = settings.ROBOKASSA_PASSWORD2

        out_sum = request_data.get('OutSum')
        inv_id = request_data.get('InvId')
        received_signature = request_data.get('SignatureValue')

        shp_params = {}
        for key, value in request_data.items():
            if key.startswith('Shp_'):
                shp_params[key] = value

        signature_string = f"{out_sum}:{inv_id}:{password}"
        sorted_shp_params = sorted(shp_params.items())
        for key, value in sorted_shp_params:
            signature_string += f":{key}={value}"
        calculated_signature = hashlib.md5(signature_string.encode()).hexdigest().lower()
        return calculated_signature == received_signature.lower()

    @staticmethod
    def process_payment(payment_data):
        try:
            inv_id = payment_data.get('InvId')
            out_sum = payment_data.get('OutSum')

            user_id = payment_data.get('Shp_user_id')
            subscription_service_id = payment_data.get('Shp_subscription_service')
            subscription_period_id = payment_data.get('Shp_subscription_period')
            console_type_id = payment_data.get('Shp_console_type')

            payment = Payment.objects.get(invoice_id=inv_id)

            if float(payment.amount) != float(out_sum):
                payment.status = 'failed'
                payment.save()
                return False, "Сумма платежа не соответствует"
            payment.status = 'success'
            payment.save()

            if not payment.subscription:
                subscription = Subscription.objects.create(
                    user_id=user_id,
                    subscription_service_id=subscription_service_id,
                    subscription_period_id=subscription_period_id,
                    console_type_id=console_type_id,
                    is_active=True
                )

                payment.subscription = subscription
                payment.save()
            else:
                subscription = payment.subscription
                subscription.is_active = True
                subscription.save()

            return True, "Платеж успешно обработан"

        except Payment.DoesNotExist:
            return False, "Платеж не найден"
        except Exception as e:
            return False, f"Ошибка при обработке платежа: {str(e)}"

    @staticmethod
    def create_payment(user, subscription_service, subscription_period, console_type):
        invoice_id = RobokassaService.generate_invoice_id()
        amount = subscription_period.price
        description = f"Подписка {subscription_service.name} ({subscription_service.choices_level}) на {subscription_period.months} мес."
        payment = Payment.objects.create(
            user=user,
            amount=amount,
            description=description,
            invoice_id=invoice_id,
            subscription_service=subscription_service,
            subscription_period=subscription_period,
            console_type=console_type,
            status='pending'
        )

        return payment