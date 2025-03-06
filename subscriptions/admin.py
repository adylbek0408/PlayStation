from django.contrib import admin
from .models import ConsoleType, SubscriptionService, SubscriptionContent, SubscriptionPeriod, Subscription, Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice_id', 'user', 'amount', 'status', 'created_at', 'subscription_service',
                    'subscription_period']
    list_filter = ['status', 'subscription_service', 'console_type']
    search_fields = ['invoice_id', 'user__username', 'description']
    readonly_fields = ['invoice_id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Основная информация', {
            'fields': ('invoice_id', 'user', 'amount', 'description', 'status')
        }),
        ('Подписка', {
            'fields': ('subscription', 'subscription_service', 'subscription_period', 'console_type')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )


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
