
from django.views.generic import DetailView

from FlowerShop import settings
from .models import Bouquet, Consultation, Order

from django.shortcuts import render, redirect, get_object_or_404


from yookassa import Configuration, Payment


def create_payment(request):
    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY
    bouquet_id = request.session.get('bouquet_id')
    bouquet = get_object_or_404(Bouquet, id=bouquet_id)
    amount = bouquet.get_price()
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
    if 'bouquet_id' in request.session:
        del request.session['bouquet_id']

    return redirect(payment.confirmation.confirmation_url)


def home(request):
    bouquets = list(Bouquet.objects.all())
    first_row = bouquets[:3]
    return render(request, 'index.html', {'first_row': first_row})

class BouquetDetailView(DetailView):
    model = Bouquet
    template_name = 'card.html'
    context_object_name = 'bouquet'

def create_order(request, ):

    if request.method == 'POST':
        name = request.POST.get('fname')
        phone = request.POST.get('tel')
        address = request.POST.get('adres')
        delivery_time = request.POST.get('orderTime')
        bouquet_id = request.POST.get('bouquet_id')
        bouquet = get_object_or_404(Bouquet, id=bouquet_id)


        Order.objects.create(
            customer_name=name,
            customer_phone=phone,
            delivery_address=address,
            delivery_time=delivery_time,
            bouquet=bouquet,

        )
        request.session['bouquet_id'] = bouquet_id
        return redirect('payment' )
    bouquet_id = request.GET.get('bouquet_id')
    return render(request, 'order.html', {'bouquet_id': bouquet_id})

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


# def get_recommendations(request):
    # all_bouquets = list(Bouquet.objects.all())
    # if not all_bouquets:
    #     return render(request, 'card.html', {'bouquet': None})
    # random_bouquet = random.choice(all_bouquets)
    #
    # return render(request, 'card.html', {
    #     'bouquet': random_bouquet,
    # })  card.html это detail букета я написал класс для отображения детальной информации по букету



# =============================Еще не сделано=============================

def get_quiz_first(request):
    return render(request, 'quiz.html')


def get_quiz_second(request):
    return render(request, 'quiz-step.html')


def make_order(request):
    return render(request, 'result.html')
