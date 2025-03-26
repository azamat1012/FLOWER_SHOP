from django.shortcuts import render


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
