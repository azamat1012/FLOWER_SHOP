from django.contrib import admin
from .models import (
    Staff,
    Customer,
    Bouquet,
    Component,
    BouquetComponent,
    Order,
    Event,
    PriceRange,
    Consultation,
)
from django.utils.html import format_html
from django.contrib.admin import action


# Register your models here.
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ["name", "role", "slug", "phone", "on_vacation"]
    list_filter = ["role", "on_vacation"]
    search_fields = ["name"]
    ordering = ["role", "name"]


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ["name", "phone"]
    list_filter = ["created_at"]
    search_fields = ["created_at"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "phone"]
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "image_preview", "note", "stock"]
    list_filter = ["type"]
    search_fields = ["name", "stock"]
    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{url}" style="max-width: {max_width}px; max-height: {max_height}px; width: auto; height: auto;"/>',
                max_width=200,
                max_height=200,
                url=obj.image.url,
            )
        return "No Image"

    image_preview.short_description = "Превью изображения"


class BouquetComponentInline(admin.TabularInline):
    model = BouquetComponent
    extra = 0
    fields = ("component", "quantity")


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    inlines = [BouquetComponentInline]
    list_display = [
        "name",
        "total_price",
        "view_composition",
        "view_events",
    ]
    list_filter = ["events"]
    readonly_fields = ["image_preview", "view_composition", "total_price"]
    search_fields = ["name", "events", "total_price"]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        bouquet = form.instance
        bouquet.total_price = bouquet.get_price()
        bouquet.save(update_fields=["total_price"])

    def view_events(self, obj):
        return ", ".join(f"{event}" for event in obj.events.all())

    view_events.short_description = "События"

    def view_composition(self, obj):
        return ", ".join(f"{name} - {qty} шт." for name, qty in obj.composition())

    view_composition.short_description = "Состав композиции"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{url}" style="max-width: {max_width}px; max-height: {max_height}px; width: auto; height: auto;"/>',
                max_width=200,
                max_height=200,
                url=obj.image.url,
            )
        return "No Image"

    image_preview.short_description = "Превью изображения"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "customer_name",
        "customer_phone",
        "delivery_address",
        "delivery_time",
        "bouquet",
        "created_at",
    ]
    search_fields = [
        "customer_name",
        "customer_phone",
        "delivery_address",
        "delivery_time",
        "bouquet",
        "created_at",
    ]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(PriceRange)
class PriceRangeAdmin(admin.ModelAdmin):
    list_display = ["name", "min_price", "max_price"]
    search_fields = ["name"]
