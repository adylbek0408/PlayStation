from django.db import models
from django.contrib.auth.models import User


class ConsoleType(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип консоли"
        verbose_name_plural = "Типы консолей"


class SubscriptionService(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    consoles = models.ManyToManyField(ConsoleType, related_name="subscriptions", verbose_name="Консоли")
    CHOICES_LEVEL = (
        ('Essential', 'Essential'),
        ('Extra', 'Extra'),
        ('Deluxe', 'Deluxe'),
    )
    choices_level = models.CharField(max_length=70, choices=CHOICES_LEVEL, verbose_name="Уровень подписки")
    image = models.FileField(verbose_name="Изображение")

    def __str__(self):
        return f"{self.name} - {self.choices_level}"

    class Meta:
        verbose_name = "Сервис подписки"
        verbose_name_plural = "Сервисы подписок"


class SubscriptionContent(models.Model):
    subscription_service = models.ForeignKey(SubscriptionService, on_delete=models.CASCADE, related_name="contents", verbose_name="Сервис подписки")
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    icon = models.FileField(verbose_name="Иконка")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Содержимое подписки"
        verbose_name_plural = "Содержимое подписок"


class SubscriptionPeriod(models.Model):
    months = models.IntegerField(verbose_name="Количество месяцев")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    subscription_service = models.ForeignKey(SubscriptionService, on_delete=models.CASCADE, related_name="periods", verbose_name="Сервис подписки")

    def __str__(self):
        return f"{self.months} - {self.price}"

    class Meta:
        verbose_name = "Период подписки"
        verbose_name_plural = "Периоды подписки"


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions", verbose_name="Пользователь")
    subscription_service = models.ForeignKey(SubscriptionService, on_delete=models.CASCADE,
                                             related_name="user_subscriptions", verbose_name="Сервис подписки")
    subscription_period = models.ForeignKey(SubscriptionPeriod, on_delete=models.CASCADE,
                                            related_name="subscriptions", verbose_name="Период подписки")
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата начала")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    console_type = models.ForeignKey(ConsoleType, on_delete=models.CASCADE,
                                     related_name="user_subscriptions", verbose_name="Тип консоли")

    def __str__(self):
        return f"{self.user.username} - {self.subscription_service.name} - {self.subscription_period.months} месяцев"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"


class Payment(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments', null=True,
                                     blank=True, verbose_name="Подписка")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', verbose_name="Пользователь")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    description = models.CharField(max_length=255, verbose_name="Описание")
    invoice_id = models.CharField(max_length=100, unique=True, verbose_name="ID счета")
    status = models.CharField(max_length=20, default='pending', verbose_name="Статус", choices=[
        ('pending', 'Ожидает оплаты'),
        ('success', 'Оплачен'),
        ('failed', 'Ошибка оплаты'),
    ])
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    subscription_service = models.ForeignKey(SubscriptionService, on_delete=models.CASCADE, related_name='payments', verbose_name="Сервис подписки")
    subscription_period = models.ForeignKey(SubscriptionPeriod, on_delete=models.CASCADE, related_name='payments', verbose_name="Период подписки")
    console_type = models.ForeignKey(ConsoleType, on_delete=models.CASCADE, related_name='payments', verbose_name="Тип консоли")

    def __str__(self):
        return f"Платеж {self.invoice_id} - {self.status}"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        