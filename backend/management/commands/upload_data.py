from django.core.management.base import BaseCommand
import json
from backend.models import Component, Bouquet, BouquetComponent, Event, PriceRange
from django.db import transaction
from django.core.files import File
from pathlib import Path
from django.conf import settings
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = "Загружает данные букетов из JSON файла в БД"

    def add_arguments(self, parser):
        parser.add_argument(
            "bouquet_json", type=str, help="Путь к JSON файлу с букетами"
        )
        parser.add_argument(
            "--media-root",
            type=str,
            help="Путь к папке с изображениями",
            default=settings.MEDIA_ROOT,
        )

    def handle(self, *args, **options):
        json_file = options["bouquet_json"]
        media_root = options.get("media_root", "")

        try:
            with open(json_file, "r", encoding="utf-8") as jfile:
                data = json.load(jfile)

            with transaction.atomic():
                
                for price_item in data.get("prices", []):
                    min_price = price_item.get("min_price", 0)
                    max_price = price_item.get("max_price", 0)
                    price, created = PriceRange.objects.get_or_create(min_price=min_price, max_price=max_price)
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"Добавлен интервал цен: {price.name}")
                        )

                        

                components = {}
                for component_data in data.get("components", []):
                    component, created = Component.objects.get_or_create(
                        name=component_data["name"],
                        defaults={
                            "type": component_data["type"],
                            "price": component_data["price"],
                            "note": component_data.get("note", ""),
                            "stock": component_data.get("stock", 0),
                        },
                    )

                    if component_data.get("image") and media_root:
                        image_path = Path(media_root) / component_data["image"]
                        if image_path.exists():
                            with open(image_path, "rb") as img_file:
                                component.image.save(
                                    component_data["image"], File(img_file), save=True
                                )
                                
                    components[component.name] = component
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"Добавлен компонент: {component.name}")
                        )

                for bouquet_data in data.get("bouquets", []):
                    bouquet_name = bouquet_data.get("name")
                    bouquet_base_price = bouquet_data.get("base_price")
                    bouquet_image = bouquet_data.get("image")
                    bouquet_description = bouquet_data.get("description")

                    bouquet, created = Bouquet.objects.get_or_create(
                        name=bouquet_name,
                        defaults={
                            "base_price": bouquet_base_price,
                            "description": bouquet_description,
                        },
                    )

                    if bouquet_data.get("image") and media_root:
                        image_path = Path(media_root) / bouquet_image
                        if image_path.exists():
                            with open(image_path, "rb") as img_file:
                                bouquet.image.save(
                                    bouquet_data["image"], File(img_file), save=True
                                )
                        else:
                            image_path = Path(media_root) / 'images/default.jpg'
                            with open(image_path, "rb") as img_file:
                                bouquet.image.save(
                                    bouquet_data["image"], File(img_file), save=True
                                )

                    for event_name in bouquet_data.get("events", []):
                        event, created = Event.objects.get_or_create(name=event_name)
                        bouquet.events.add(event)
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(f"Добавлено событие: {event.name}")
                            )

                    for component_item in bouquet_data.get("components", []):
                        component_name = component_item["name"]
                        component_quantity = component_item.get("quantity")
                        if component_name in components:
                            bouquet_component, created = (
                                BouquetComponent.objects.get_or_create(
                                    bouquet=bouquet,
                                    component=components[component_name],
                                    defaults={"quantity": component_quantity},
                                )
                            )

                            if created:
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"Компонент '{component_name}' добавлен в букет '{bouquet_name}'"
                                    )
                                )
                            else:
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"Обновлено количество '{component_name}' в букете '{bouquet_name}' - {component_quantity}"
                                    )
                                )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Компонента '{component_name}' нет в базе"
                                )
                            )

                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"Добавлен букет: {bouquet_name}")
                        )
                    bouquet.save()

            self.stdout.write(self.style.SUCCESS("Загрузка данных завершена!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {str(e)}"))
            raise
