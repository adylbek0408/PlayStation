from django.db import models
from django.contrib.auth.models import User


class ConsoleType(models.Model):
    name = models.CharField(max_length=50)  # PS4, PS5

    def __str__(self):
        return self.name


class SubscriptionService(models.Model):
    name = models.CharField(max_length=100)
    consoles = models.ManyToManyField(ConsoleType, related_name="subscriptions")
    CHOICES_LEVEL = (
        ('Essential', 'Essential'),
        ('Extra', 'Extra'),
        ('Deluxe', 'Deluxe'),
    )
    choices_level = models.CharField(max_length=70, choices=CHOICES_LEVEL)
    image = models.ImageField()

    def __str__(self):
        return self.name


class SubscriptionContent(models.Model):
    subscription_service = models.ForeignKey(SubscriptionService, on_delete=models.CASCADE, related_name="contents")
    title = models.CharField(max_length=100)
    icon = models.FileField()


class SubscriptionPeriod(models.Model):
    months = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subscription_service = models.ForeignKey(SubscriptionService, on_delete=models.CASCADE, related_name="periods")


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    subscription_service = models.ForeignKey(SubscriptionService, on_delete=models.CASCADE,
                                             related_name="user_subscriptions")
    subscription_period = models.ForeignKey(SubscriptionPeriod, on_delete=models.CASCADE,
                                            related_name="subscriptions")
    start_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    console_type = models.ForeignKey(ConsoleType, on_delete=models.CASCADE,
                                     related_name="user_subscriptions")

    def __str__(self):
        return f"{self.user.username} - {self.subscription_service.name} - {self.subscription_period.months} months"
