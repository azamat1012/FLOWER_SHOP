from django.shortcuts import render, redirect

from yookassa import Configuration, Payment

from FlowerShop import settings


def create_payment(request):
    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    payment = Payment.create({
        "amount": {
            "value": '100',
            "currency": "RUB"
        },
        "capture_mode": "AUTOMATIC",
        "confirmation": {
            "type": "redirect",
            "return_url": "http://127.0.0.1:8000/"
        },
        "description": f"Оплата заказа на сумму 100 руб."
    })

    return redirect(payment.confirmation.confirmation_url)
def home(request):
    return render(request, 'index.html')


def get_catalog(request):
    return render(request, 'catalog.html')


def get_quiz_first(request):
    return render(request, 'quiz.html')


def get_quiz_second(request):
    return render(request, 'quiz-step.html')


def get_consultation(request):
    return render(request, 'consultation.html')


def get_recommendations(request):
    return render(request, 'card.html')


def get_order_first(request):
    return render(request, 'order.html')


def get_order_second(request):
    return render(request, 'order-step.html')


def make_order(request):
    return render(request, 'result.html')
