from rest_framework import serializers
from .models import ConsoleType, SubscriptionService, SubscriptionContent, SubscriptionPeriod, Subscription
from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    service_name = serializers.SerializerMethodField()
    service_level = serializers.SerializerMethodField()
    period_months = serializers.SerializerMethodField()
    console_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'invoice_id', 'amount', 'description', 'status',
            'created_at', 'updated_at', 'service_name', 'service_level',
            'period_months', 'console_name'
        ]
        read_only_fields = [
            'invoice_id', 'status', 'created_at', 'updated_at'
        ]

    def get_service_name(self, obj):
        return obj.subscription_service.name

    def get_service_level(self, obj):
        return obj.subscription_service.choices_level

    def get_period_months(self, obj):
        return obj.subscription_period.months

    def get_console_name(self, obj):
        return obj.console_type.name


class PaymentInitiateSerializer(serializers.Serializer):
    subscription_service_id = serializers.IntegerField()
    subscription_period_id = serializers.IntegerField()
    console_type_id = serializers.IntegerField()


class ConsoleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsoleType
        fields = '__all__'


class SubscriptionContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionContent
        fields = ['title', 'icon']


class SubscriptionPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPeriod
        fields = ['months', 'price']


class SubscriptionServiceSerializer(serializers.ModelSerializer):
    contents = SubscriptionContentSerializer(many=True, read_only=True)
    periods = SubscriptionPeriodSerializer(many=True, read_only=True)

    class Meta:
        model = SubscriptionService
        fields = ['id', 'name', 'consoles', 'choices_level', 'image', 'contents', 'periods']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'subscription_service', 'subscription_period',
                  'start_date', 'is_active', 'console_type']
        read_only_fields = ['start_date']

