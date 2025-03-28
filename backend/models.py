from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


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

    name = models.CharField(verbose_name="ФИО", max_length=50)
    phone = PhoneNumberField(verbose_name="Телефон", unique=True)

    def __str__(self):
        return f"{self.name}-{self.pk}"

    class Meta:
        unique_together = ["name", "phone"]
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
    name = models.CharField(verbose_name="Название", max_length=50, unique=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=1.00, verbose_name="Стоимость (руб.)"
    )
    image = models.ImageField(verbose_name="Изображение", blank=True, null=True)
    note = models.CharField(
        verbose_name="Примечания",
        max_length=100,
        blank=True,
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Стоковое количество")

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ["name", "price"]
        verbose_name = "Элемент"
        verbose_name_plural = "Элементы"
        ordering = ["type"]


class Bouquet(models.Model):
    """Модель букета"""

    name = models.CharField(verbose_name="Название", max_length=50, unique=True)
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1.00,
        verbose_name="Стоимость оформления (руб.)",
    )
    image = models.ImageField(verbose_name="Изображение", blank=True, null=True)
    description = models.CharField(verbose_name="описание", max_length=100)
    events = models.ManyToManyField(
        "Event", related_name="bouquets", verbose_name="События", blank=True
    )   
    

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
    """Модель заказа"""

    bouquet = models.ForeignKey(
        "Bouquet", verbose_name="Букет", on_delete=models.PROTECT
    )
    client = models.ForeignKey(
        "Customer",
        verbose_name="Клиент",
        on_delete=models.CASCADE,
        related_name="client_orders",
    )
    flowerist = models.ForeignKey(
        "Staff",
        verbose_name="Флорист",
        on_delete=models.CASCADE,
        related_name="flowerist_orders",
        limit_choices_to={"role": "flowerist"},
    )
    courier = models.ForeignKey(
        "Staff",
        verbose_name="Курьер",
        on_delete=models.CASCADE,
        related_name="courier_orders",
        limit_choices_to={"role": "courier"},
    )
    address = models.TextField(verbose_name="Адрес")
    desired_date = models.DateTimeField(verbose_name="Дата")
    desired_time = models.TimeField(verbose_name="Время")
    flowerist_comment = models.CharField(
        max_length=200, verbose_name="Комментарии флористу", blank=True, null=True
    )
    delivery_comment = models.CharField(
        max_length=200, verbose_name="Комментарии курьеру", blank=True, null=True
    )
    total_cost = models.FloatField(verbose_name="Общая стоимость", default=0.0)
    created_at = models.DateTimeField(
        verbose_name="Дата создания заказа", default=timezone.now
    )

    def __str__(self):
        return f"{self.pk} - {self.client.name} {self.created_at}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class Event(models.Model):

    name = models.CharField(max_length=200, verbose_name="Тип события")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"


class PriceInterval(models.Model):

    min_price = models.PositiveIntegerField(
        verbose_name="Минимальная цена", unique=True, default=0
    )
    max_price = models.PositiveIntegerField(
        verbose_name="Максимальная цена", unique=True, default=1
    )

    def __str__(self):
        return f"{self.min_price} - {self.max_price}"

    def clean(self):
        if self.min_price > 99999:
            raise ValidationError("Минимальная цена не может превышать 99 999")

        if self.max_price > 100000:
            raise ValidationError("Максимальная цена не может превышать 100 000")

        if self.min_price >= self.max_price:
            raise ValidationError("Минимальная цена должна быть меньше максимальной")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Ценовой интервал"
        verbose_name_plural = "Ценовые интервалы"
        ordering = ["min_price"]
