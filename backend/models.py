from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.core.validators import MinValueValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings
from pathlib import Path


class Staff(models.Model):
    """Модель персонала, связанная с пользователями Django"""

    ROLE_CHOICES = [
        ("flowerist", "Флорист"),
        ("courier", "Курьер"),
    ]

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, verbose_name="Должность"
    )
    slug = models.SlugField(
        max_length=225, verbose_name="ID персонала", unique=True, blank=True, null=True
    )
    name = models.CharField(verbose_name="ФИО", max_length=50)
    phone = PhoneNumberField(
        verbose_name="Телефон", unique=True, blank=False, null=True
    )
    on_vacation = models.BooleanField(verbose_name="В отпуске", default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.user.username)
            self.slug = f"{base_slug}-{get_random_string(4)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}-{self.pk}"

    class Meta:
        unique_together = ["name", "phone"]
        verbose_name = "Персонал"
        verbose_name_plural = "Персонал"
        ordering = ["role"]


class Customer(models.Model):
    """Модель клиента, связанная с пользователями Django"""

    name = models.CharField(verbose_name="ФИО", max_length=50, unique=True)
    phone = PhoneNumberField(verbose_name="Телефон", unique=True)

    def __str__(self):
        return f"{self.name}-{self.pk}"

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Component(models.Model):
    """Модель элементов букета"""

    TYPE_CHOICES = [
        ("flower", "Цветок"),
        ("accessory", "Аксессуар"),
    ]

    type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, verbose_name="Тип элемента"
    )
    name = models.CharField(verbose_name="Название",
                            max_length=50, unique=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=1.00, verbose_name="Стоимость (руб.)"
    )
    image = models.ImageField(
        verbose_name="Изображение", blank=True, null=True)
    note = models.CharField(
        verbose_name="Примечания",
        max_length=100,
        blank=True,
    )
    stock = models.PositiveIntegerField(
        default=0, verbose_name="Стоковое количество")

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ["name", "price"]
        verbose_name = "Элемент"
        verbose_name_plural = "Элементы"
        ordering = ["type"]


class Bouquet(models.Model):
    """Модель букета"""

    name = models.CharField(verbose_name="Название",
                            max_length=50, unique=True)
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Стоимость оформления (руб.)",
    )
    image = models.ImageField(verbose_name="Изображение", null=True)
    description = models.CharField(verbose_name="описание", max_length=100)
    events = models.ManyToManyField(
        "Event", related_name="bouquets", verbose_name="События", blank=True
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Общая стоимость"
    )

    def get_price(self):
        total_price = self.base_price
        for bouquet_component in self.components.all():
            total_price += (
                bouquet_component.component.price * bouquet_component.quantity
            )
        return total_price

    def composition(self):
        return [(item.component, item.quantity) for item in self.components.all()]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Букет"
        verbose_name_plural = "Букеты"


class BouquetComponent(models.Model):
    """Связь букета с его составляющими"""

    bouquet = models.ForeignKey(
        Bouquet, on_delete=models.CASCADE, related_name="components"
    )
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)], verbose_name="Количество"
    )

    def __str__(self):
        return f"{self.bouquet.name}: {self.component.name} x {self.quantity} "

    class Meta:
        verbose_name = "Компонент букета"
        verbose_name_plural = "Компоненты букетов"
        unique_together = ["bouquet", "component"]


class Order(models.Model):
    customer_name = models.CharField(max_length=255, blank=True)
    customer_phone = models.CharField(max_length=15, blank=True)
    delivery_address = models.TextField(blank=True)
    delivery_time = models.CharField(max_length=50, blank=True)
    bouquet = models.ForeignKey(
        Bouquet, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ #{self.id} от {self.customer_name}"


class Event(models.Model):

    name = models.CharField(
        max_length=200, verbose_name="Тип события", unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"


class PriceRange(models.Model):
    name = models.CharField(
        max_length=100, help_text="Название диапазона (например, 'До 1 000 руб')"
    )
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Минимальная цена (может быть NULL для отсутствия ограничения)",
    )
    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Максимальная цена (может быть NULL для отсутствия ограничений)",
    )

    def __str__(self):
        if self.min_price and self.max_price:
            return f"{self.name} ({self.min_price} - {self.max_price})"
        elif self.min_price:
            return f"{self.name} (От {self.min_price})"
        elif self.max_price:
            return f"{self.name} (До {self.max_price})"
        return self.name


class Consultation(models.Model):
    """Модель консультации"""

    name = models.CharField(verbose_name="Имя", max_length=50)
    phone = PhoneNumberField(verbose_name="Телефон")
    agreed_to_privacy = models.BooleanField(
        verbose_name="Согласие на обработку данных", default=False
    )
    created_at = models.DateTimeField(
        verbose_name="Дата создания", auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"

    class Meta:
        verbose_name = "Консультация"
        verbose_name_plural = "Консультации"


@receiver(pre_save, sender=Bouquet)
def calculate_price(sender, instance, **kwargs):
    if instance.pk:
        instance.total_price = instance.get_price()
