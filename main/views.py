from django import http, template
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from .models import *
import json
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
from .interkassa import interkassa_sign_check
from django.conf import settings
import random
from django.utils import timezone

NO_POSTER_TO_LOC = 'Афиша для данного кинотеарта пустая'
DEFAULT_URL_MAP = 'https://yandex.ru'

@require_POST
@csrf_exempt
def payment_result(request):# для кассы 
    if interkassa_sign_check(request.POST, settings.INTERKASSA_SECRET): #проверяем сигнатуру
        ik_co_id = request.POST.get('ik_co_id')
        if ik_co_id and ik_co_id == settings.INTERKASSA_ID:    # проверяем номер кассы
            ik_pm_no = request.POST.get('ik_pm_no')
            if ik_pm_no:
                pt = PurchasedTickets.objects.filter(payment_number=ik_pm_no) #запрашиваем платёж в базе по номеру
                if pt: 
                    ik_inv_st = request.POST.get('ik_inv_st') #получаем состояние платежа
                    if ik_inv_st and (ik_inv_st == 'fail' or ik_inv_st == 'canceled'): #если была отмена или ошибка
                        pt[0].status = purchased_tickets_status.NOT_VALID #помечаем билет как не валидный
                        pt[0].save()
                        pt[0].film.sum_tickets += 1 #возвращаем билет к фильму обратно 
                        pt[0].film.save()
                        return HttpResponse('ok')
                    else: #если не отмена, будет считать что успех
                        pt[0].status = purchased_tickets_status.PAID #помечай билет как оплаченный 
                        pt[0].save() 
                        return HttpResponse('ok')
    return HttpResponseBadRequest('error')

def check_film_payment_(id):
    films = Films.objects.filter(id=id)   #проверка остатка билетов по ид фильма
    if films and films[0].sum_tickets > 0:
        return films[0]
    return None

def check_film_payment(request): #функция для скрипта проверки остатка билетов у фильма на афише
    id = request.GET.get('id')
    if id:
        if check_film_payment_(id):
            return HttpResponse('ok')
        return HttpResponse('no')
    return HttpResponse('no')

def gen_payment_number(): #генератор номера оплаты
    while True:
        num = random.randint(1, 10000000) #генерируем случайно число от 1 до 10000000
        if not PurchasedTickets.objects.filter(payment_number=num):# делаем запрос, если с таким номером
            return num #если нету возвращаем номер

@csrf_protect
def payment(request): #функция оплаты, проверяем все ли данные пришли от формы офорления билетов
    if 'id_film' in request.POST and 'name' in request.POST and 'phone' in request.POST and 'number_car' in request.POST:
        id_film = request.POST.get('id_film')
        film = check_film_payment_(id_film) #проверяем, остались ли билеты для продажи
        if film:
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            number_car = request.POST.get('number_car')
            #создаём в базе билет 
            pt = PurchasedTickets(payment_number=gen_payment_number(), date_session=film.date,
            number_telephone=phone, number_car=number_car, status=purchased_tickets_status.WAIT_PAYMENT, film=film)
            form = { 'ik_co_id' : settings.INTERKASSA_ID, 'ik_pm_no' : pt.payment_number,
            'ik_am' : film.price,
            'ik_desc' : 'Покупка билета на фильм: ' + film.title }
            pt.save()
            film.sum_tickets -= 1
            film.save()
            return render(request, 'main/form_payment.html', form )
        return HttpResponseBadRequest('no payment film')

    return HttpResponseBadRequest('form inpur error')

def f_get_url_map_cookies(cookies): #функция получение ссылки на карту, для остальный страниц сайта
    id = cookies.get('kino_loc_id')
    loc = None
    if id:
        loc = KinoLocation.objects.filter(id=id)
    else:
        loc = KinoLocation.objects.all()

    if loc:
        return loc[0].urlMap
    else:
        return DEFAULT_URL_MAP

@csrf_exempt
def fail_payment(request):
    context = { 'urlMap' : f_get_url_map_cookies(request.COOKIES) }
    return render(request, 'main/fail_payment.html', context)

@csrf_exempt
def succes_payment(request):
    context = { 'urlMap' : f_get_url_map_cookies(request.COOKIES) }
    return render(request, 'main/succes_payment.html', context)

def contacts(request):
    context = { 'urlMap' : f_get_url_map_cookies(request.COOKIES) }
    return render(request, 'main/contacts.html', context)

def faq(request):
    faq = FAQ.objects.all()
    context = { 'faq': faq, 'urlMap' : f_get_url_map_cookies(request.COOKIES) }
    return render(request, 'main/faq.html', context)

def about(request):
    context = { 'urlMap' : f_get_url_map_cookies(request.COOKIES) }
    return render(request, 'main/about.html', context)

def get_films(request): #функция страницы для обновления фильмов
    id = request.GET.get('id') #получаем ид локации из запроса
    error = 'error_007'
    if id:
        cur_kino_loc = KinoLocation.objects.filter(id=id) #получаем локацию из бд по ид
        if cur_kino_loc: #проверям, получили или нет из бд
            films = Films.objects.filter(loc=cur_kino_loc[0]) #получаем фильмы по локации
            if films: #если фильмы есть, собираем шаблон и записываем это в json виде
                json_data = { 'html' : render_to_string('main/poster_films.html', {'films' : films}),
                'map' : cur_kino_loc[0].urlMap } #также передаём ссылку на карту
                resp = HttpResponse( json.dumps(json_data) )
                resp.set_cookie('kino_loc_id', id) #сохранём в куки ид локации выбранной пользователем
                return resp #возвращаем ответ 
            else:
                return HttpResponse(NO_POSTER_TO_LOC)
        else: #если локации нету по указанному ид, возвращаем ошибку
            return HttpResponse(error)
    else: #если не передан был айди, возвращаем ошибку
        return HttpResponse(error)

def get_films_poster(): #получаем фильмы, на текущей момент, которые находятся в афише
                        #и также будет отсикать те, у которых уже начался показ
    films = Films.objects.filter(status='poster') #получаем фильмы которые в афишах
    current_time = timezone.now() #получаем текущее время на сервере
    return films

def index(request):
    films_poster = get_films_poster()
    kino_loc_user_id = request.COOKIES.get('kino_loc_id') #получаем из куков номер ид кино
    context_index = { 'films' : '', 'select_kino' : None, 'cur_kino_id' : -1, 'urlMap' : DEFAULT_URL_MAP }
    #заполняем контекст для шаблона index 

    kino_location = KinoLocation.objects.all() #получаем из базы все локация
    if kino_location: #если они есть 
        context_index['select_kino'] = kino_location #записываем их для шаблона
        if kino_loc_user_id == None: #если в куках не было ид кино, то тогда выбираем самую первую локацию
            kino_loc_user_id = kino_location[0].id
        else:
            kino_loc_user_id = int(kino_loc_user_id)   #если же оказалось, то записываем для шаблона
            context_index['cur_kino_id'] = kino_loc_user_id
    else:
        kino_loc_user_id = None #если нету локаций помечаем через данную переменную

    if kino_loc_user_id:  #понимаем, если были локации, то получаем локацию в полном виде модели
        cur_kino_loc = KinoLocation.objects.filter(id=kino_loc_user_id)
        context_index['urlMap'] = cur_kino_loc[0].urlMap #записываем ссылку карты, для шаблона
        films = films_poster.filter(loc=cur_kino_loc[0]) #получаем фильм по выбранной локации
        if films: # если есть, то собираем шаблон афиши фильмов
            context_index['films'] = render_to_string('main/poster_films.html', {'films' : films})
        else: #если нету, пишем что нету
            context_index['films'] = NO_POSTER_TO_LOC
    else: #если оказалось что нету локаций, то пишем это
        context_index['films'] = 'Афиша пустая'

    return render(request, 'main/index.html', context_index) #собираем шаблон index и возвращаем