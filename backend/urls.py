
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.home, name='home'),

    path('catalog/', views.get_catalog, name='catalog'),
    path('recommendation/', views.get_recommendations, name='recommendation'),
    path('quiz/', views.get_quiz_first, name='quiz_1'),
    path('quiz/2', views.get_quiz_second, name='quiz_2'),
    path('consultation/', views.get_consultation, name='consultation'),
    path('order/', views.get_order_first, name="order_1"),
    path('order/2/', views.get_order_second, name="order_2"),

    path('make_order/', views.make_order, name='result'),
    path('payment/', views.create_payment, name='payment'),
]
