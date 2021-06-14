from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('films', views.get_films, name='get_films'),
    path('contacts', views.contacts, name='contacts'),
    path('faq', views.faq, name='faq'),
    path('about', views.about, name='about'),
    path('payment_result', views.payment_result, name='result'),
    path('payment', views.payment, name='payment'),
    path('check_film_payment', views.check_film_payment, name='check_film_payment'),
    path('succes_payment', views.succes_payment, name='succes_payment'),
    path('fail_payment', views.fail_payment, name='fail_payment')
]