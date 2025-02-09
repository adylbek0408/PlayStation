from django.contrib import admin
from .models import ConsoleType, SubscriptionService, SubscriptionContent, SubscriptionPeriod, Subscription


class SubscriptionContentInline(admin.StackedInline):
    model = SubscriptionContent
    extra = 1


class SubscriptionPeriodInline(admin.TabularInline):
    model = SubscriptionPeriod
    extra = 1


@admin.register(ConsoleType)
class ConsoleTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(SubscriptionService)
class SubscriptionServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'choices_level']
    inlines = [SubscriptionContentInline, SubscriptionPeriodInline]
    filter_horizontal = ['consoles']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription_service', 'subscription_period', 'start_date', 'is_active', 'console_type']
    list_filter = ['is_active', 'console_type', 'subscription_service']
    search_fields = ['user__username']
