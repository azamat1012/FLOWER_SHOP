
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),

    path('catalog/', views.get_catalog, name='catalog'),
    # path('recommendation/', views.get_recommendations, name='recommendation'),
    path('quiz/', views.get_quiz_first, name='quiz_1'),
    path('quiz/2', views.get_quiz_second, name='quiz_2'),
    path('consultation/', views.get_consultation, name='consultation'),
    path('create-order/', views.create_order, name="create_order"),

    path('make_order/', views.quiz_results, name='result'),
    path('payment/', views.create_payment, name='payment'),
    path('bouquet/<int:pk>/', views.BouquetDetailView.as_view(), name='bouquet_detail')
]
