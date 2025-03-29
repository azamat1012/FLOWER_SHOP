import random

from FlowerShop import settings
from .models import Bouquet, Consultation, Customer, Staff, Order

from django.shortcuts import render, redirect
from django.utils import timezone

from yookassa import Configuration, Payment


def create_payment(request, amount):
    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    payment = Payment.create({
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "capture_mode": "AUTOMATIC",
        "confirmation": {
            "type": "redirect",
            "return_url": "http://127.0.0.1:8000/   "
        },
        "description": f"Оплата заказа на сумму {amount} руб."
    })
    if 'order_data' in request.session:
        del request.session['order_data']

    return redirect(payment.confirmation.confirmation_url)


def home(request):
    bouquets = list(Bouquet.objects.all())
    first_row = bouquets[:3]
    return render(request, 'index.html', {'first_row': first_row})


def get_catalog(request):
    bouquets = list(Bouquet.objects.all())
    first_row = bouquets[:3]
    second_row = bouquets[3:6] if len(bouquets) > 3 else None

    return render(request, 'catalog.html', {
        'first_row': first_row,
        'second_row': second_row
    })


def get_consultation(request):
    if request.method == 'POST':
        name = request.POST.get('fname')
        phone = request.POST.get('tel')
        Consultation.objects.create(
            name=name,
            phone=phone,
        )

        return redirect('home')

    return render(request, 'consultation.html')


def get_recommendations(request):
    all_bouquets = list(Bouquet.objects.all())
    if not all_bouquets:
        return render(request, 'card.html', {'bouquet': None})
    random_bouquet = random.choice(all_bouquets)

    return render(request, 'card.html', {
        'bouquet': random_bouquet,
    })


def get_order_first(request):
    bouquet_id = request.GET.get('bouquet_id')
    if not bouquet_id:
        print("Пользователь не выбрал еще букет")
        return redirect('recommendation')

    try:
        bouquet = Bouquet.objects.get(id=bouquet_id)
    except Bouquet.DoesNotExist:
        return redirect('recommendation')

    if request.method == "POST":
        name = request.POST.get('fname')
        phone = request.POST.get('tel')
        address = request.POST.get('adres')
        delivery_time = request.POST.get('orderTime')

        request.session['order_data'] = {               # session - что-то типа словаря для временного хранения данных
            'bouquet_id': bouquet_id,
            'name': name,
            'phone': phone,
            'address': address,
            'delivery_time': delivery_time
        }
        return redirect('order_2')
    return render(request, 'order.html', {'bouquet': bouquet})


def get_order_second(request):
    order_data = request.session.get('order_data')

    if not order_data:
        print("Нет данных заказа в сессии")
        return redirect('order_1')

    try:
        bouquet = Bouquet.objects.get(id=order_data['bouquet_id'])
    except (Bouquet.DoesNotExist, KeyError) as e:
        print("ОШИБКА ПРИ ОФОРМЛЕНИИ ЗАКАЗА (order-step.html):", e)
        return redirect('recommendation')

    if request.method == 'POST':
        try:
            customer, created = Customer.objects.get_or_create(
                name=order_data['name'],
                phone=order_data['phone']
            )
            florist = random.choice(Staff.objects.filter(
                role='flowerist', on_vacation=False))
            courier = random.choice(Staff.objects.filter(
                role='courier', on_vacation=False))
            order = Order.objects.create(
                bouquet=bouquet,
                client=customer,
                flowerist=florist,
                courier=courier,
                address=order_data['address'],
                desired_date=timezone.now(),
                desired_time=order_data['delivery_time'],
                total_cost=bouquet.get_price()
            )
            return create_payment(request, order.total_cost)

        except Exception as e:
            print("ОШИБКА ПРИ ОФОРМЛЕНИИ ЗАКАЗА (order-step.html):", e)
            return redirect('order_1')
    return render(request, 'order-step.html', {'bouquet': bouquet})


# =============================Еще не сделано=============================

def get_quiz_first(request):
    return render(request, 'quiz.html')


def get_quiz_second(request):
    return render(request, 'quiz-step.html')


def make_order(request):
    return render(request, 'result.html')
