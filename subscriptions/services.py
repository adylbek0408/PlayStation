import hashlib
import uuid
import sys
import time
import os
from urllib.parse import urlencode
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import Payment, Subscription
import logging
from datetime import datetime

log_dir = os.path.expanduser('~/robokassa_logs')
os.makedirs(log_dir, exist_ok=True)

file_handler = logging.FileHandler(os.path.join(log_dir, f'robokassa_debug_{datetime.now().strftime("%Y%m%d")}.log'))
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

logger = logging.getLogger('robokassa')
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.propagate = False


class RobokassaService:
    @staticmethod
    def generate_invoice_id():
        invoice_id = str(int(time.time()) % 100000)
        logger.debug(f"Сгенерирован InvId: {invoice_id}")
        return invoice_id

    @staticmethod
    def get_payment_url(payment, merchant_login=None):
        logger.info(f"=== НАЧАЛО СОЗДАНИЯ ПЛАТЕЖНОГО URL ===")

        if merchant_login is None:
            merchant_login = settings.ROBOKASSA_MERCHANT_LOGIN

        password = settings.ROBOKASSA_TEST_PASSWORD1 if settings.ROBOKASSA_TEST_MODE else settings.ROBOKASSA_PASSWORD1

        invoice_id = payment.invoice_id
        amount = payment.amount
        description = payment.description

        logger.info(f"MerchantLogin: {merchant_login}")
        logger.info(f"OutSum (raw): {amount} (type: {type(amount)})")
        logger.info(f"InvId: {invoice_id}")
        logger.info(f"Password1: {password[:3]}...{password[-3:]}")
        logger.info(f"Description: {description}")
        logger.info(f"Using test mode: {settings.ROBOKASSA_TEST_MODE}")

        amount_str = f"{float(amount):.2f}".replace(',', '.')
        logger.info(f"Formatted OutSum: {amount_str}")

        base_signature = f"{merchant_login}:{amount_str}:{invoice_id}:{password}"
        logger.info(f"Base signature string: {base_signature}")

        shp_params = {
            'Shp_user_id': payment.user.id,
            'Shp_subscription_service': payment.subscription_service.id,
            'Shp_subscription_period': payment.subscription_period.id,
            'Shp_console_type': payment.console_type.id,
        }

        sorted_shp_params = sorted(shp_params.items())

        signature_value = base_signature
        for key, value in sorted_shp_params:
            signature_value += f":{key}={value}"

        logger.info(f"Full signature string: {signature_value}")

        signature = hashlib.md5(signature_value.encode('utf-8')).hexdigest().lower()
        logger.info(f"MD5 hash: {signature}")

        params = {
            'MerchantLogin': merchant_login,
            'OutSum': amount_str,
            'InvId': invoice_id,
            'Description': description,
            'SignatureValue': signature,
            'IsTest': 1 if settings.ROBOKASSA_TEST_MODE else 0,
            'Culture': 'ru',
        }

        params.update(shp_params)

        logger.debug(f"All request params: {params}")

        base_url = 'https://auth.robokassa.ru/Merchant/Index.aspx'
        final_url = f"{base_url}?{urlencode(params)}"
        logger.info(f"Final URL: {final_url}")
        logger.info(f"URL length: {len(final_url)} chars")
        logger.info(f"=== КОНЕЦ СОЗДАНИЯ ПЛАТЕЖНОГО URL ===")

        try:
            log_path = os.path.join(log_dir, 'payment_urls.log')
            with open(log_path, 'a') as f:
                f.write(f"\n\nTime: {datetime.now()}\n")
                f.write(f"MerchantLogin: {merchant_login}\n")
                f.write(f"Payment ID: {payment.invoice_id}\n")
                f.write(f"Amount: {amount_str}\n")
                f.write(f"Signature String: {signature_value}\n")
                f.write(f"Signature: {signature}\n")
                f.write(f"URL: {final_url}\n")
            logger.debug(f"Данные платежа записаны в {log_path}")
        except Exception as e:
            logger.error(f"Error writing to log file: {e}")

        return final_url

    @staticmethod
    def check_signature(request_data):
        logger.info(f"=== ПРОВЕРКА ПОДПИСИ ОТ РОБОКАССЫ ===")
        if settings.ROBOKASSA_TEST_MODE:
            password = settings.ROBOKASSA_TEST_PASSWORD2
        else:
            password = settings.ROBOKASSA_PASSWORD2

        out_sum = request_data.get('OutSum')
        inv_id = request_data.get('InvId')
        received_signature = request_data.get('SignatureValue')

        logger.info(f"Verifying signature. OutSum: {out_sum}, InvId: {inv_id}")
        logger.info(f"Received signature: {received_signature}")
        logger.info(f"Using password2: {password[:3]}...{password[-3:]}")

        if not all([out_sum, inv_id, received_signature]):
            logger.error("Missing required parameters for signature verification")
            return False

        shp_params = {}
        for key, value in request_data.items():
            if key.startswith('Shp_'):
                shp_params[key] = value

        logger.info(f"Received Shp params: {shp_params}")

        signature_string = f"{out_sum}:{inv_id}:{password}"
        base_signature = signature_string
        logger.info(f"Base signature string for checking: {base_signature}")

        sorted_shp_params = sorted(shp_params.items())
        for key, value in sorted_shp_params:
            signature_string += f":{key}={value}"

        logger.info(f"Full signature string for checking: {signature_string}")

        calculated_signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest().lower()
        logger.info(f"Calculated signature: {calculated_signature}")
        logger.info(f"Received signature: {received_signature.lower()}")

        result = calculated_signature == received_signature.lower()
        logger.info(f"Signature match: {result}")
        logger.info(f"=== КОНЕЦ ПРОВЕРКИ ПОДПИСИ ===")

        return result

    @staticmethod
    def process_payment(payment_data):
        logger.info(f"=== ОБРАБОТКА ПЛАТЕЖА ===")
        try:
            logger.info(f"Processing payment. Data: {payment_data}")

            inv_id = payment_data.get('InvId')
            out_sum = payment_data.get('OutSum')

            user_id = payment_data.get('Shp_user_id')
            subscription_service_id = payment_data.get('Shp_subscription_service')
            subscription_period_id = payment_data.get('Shp_subscription_period')
            console_type_id = payment_data.get('Shp_console_type')

            logger.info(f"Payment ID: {inv_id}, Amount: {out_sum}")
            logger.info(
                f"User ID: {user_id}, Service ID: {subscription_service_id}, Period ID: {subscription_period_id}, Console ID: {console_type_id}")

            try:
                payment = Payment.objects.get(invoice_id=inv_id)
                logger.info(f"Found payment in DB: {payment}")
            except Payment.DoesNotExist:
                logger.error(f"Error - Payment with ID {inv_id} not found in database")
                return False, "Платеж не найден"

            payment_amount = float(payment.amount)
            received_amount = float(out_sum)

            logger.info(f"Payment amount in DB: {payment_amount}, Received amount: {received_amount}")

            if payment_amount != received_amount:
                logger.warning(f"Amount mismatch. DB: {payment_amount}, Received: {received_amount}")
                payment.status = 'failed'
                payment.save()
                return False, "Сумма платежа не соответствует"

            logger.info(f"Updating payment status to 'success'")
            payment.status = 'success'
            payment.save()

            if not payment.subscription:
                logger.info(f"Creating new subscription")
                try:
                    subscription = Subscription.objects.create(
                        user_id=user_id,
                        subscription_service_id=subscription_service_id,
                        subscription_period_id=subscription_period_id,
                        console_type_id=console_type_id,
                        is_active=True
                    )
                    logger.info(f"Subscription created: {subscription}")

                    payment.subscription = subscription
                    payment.save()
                except Exception as e:
                    logger.error(f"Error creating subscription: {e}")
                    return False, f"Ошибка при создании подписки: {str(e)}"
            else:
                logger.info(f"Activating existing subscription: {payment.subscription}")
                subscription = payment.subscription
                subscription.is_active = True
                subscription.save()

            logger.info(f"Payment processing completed successfully")
            logger.info(f"=== КОНЕЦ ОБРАБОТКИ ПЛАТЕЖА ===")
            return True, "Платеж успешно обработан"

        except Payment.DoesNotExist:
            logger.error(f"Error - Payment not found")
            return False, "Платеж не найден"
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return False, f"Ошибка при обработке платежа: {str(e)}"

    @staticmethod
    def create_payment(user, subscription_service, subscription_period, console_type):
        logger.info(f"=== СОЗДАНИЕ ПЛАТЕЖА ===")
        invoice_id = RobokassaService.generate_invoice_id()
        amount = subscription_period.price
        description = f"Подписка {subscription_service.name} ({subscription_service.choices_level}) на {subscription_period.months} мес."

        logger.info(f"Creating new payment. Invoice ID: {invoice_id}")
        logger.info(
            f"User: {user.username}, Service: {subscription_service.name}, Period: {subscription_period.months}, Amount: {amount}")

        try:
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
            logger.info(f"Payment created: {payment}")
            logger.info(f"=== КОНЕЦ СОЗДАНИЯ ПЛАТЕЖА ===")
            return payment
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            logger.info(f"=== ОШИБКА СОЗДАНИЯ ПЛАТЕЖА ===")
            raise
