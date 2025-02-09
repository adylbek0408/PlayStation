from rest_framework import serializers
from .models import ConsoleType, SubscriptionService, SubscriptionContent, SubscriptionPeriod, Subscription


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

