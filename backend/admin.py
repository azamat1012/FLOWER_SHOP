from django.contrib import admin
from .models import Staff, Customer, Bouquet, Component, BouquetComponent, Order
from django.utils.html import format_html


# Register your models here.
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ["name", "role", "slug", "phone", "on_vacation"]
    list_filter = ["role", "on_vacation"]
    search_fields = ["name"]
    ordering = ["role", "name"]


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
    fields = ('component', 'quantity') 

@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    inlines = [
        BouquetComponentInline,
    ]
    list_display = ["name", "base_price", "view_composition", "available"]
    list_filter = ["available"]
    readonly_fields = ["image_preview", "view_composition"]
    search_fields = ["name"]
    
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
    list_display = ["bouquet", "client", "flowerist", "courier", "total_cost", "created_at"]
    search_fields = ["bouquet", "client", "flowerist", "courier", "total_cost", "created_at"]