from json import encoder
from django.db import models

from embed_video.fields import EmbedVideoField

from enum import auto

class KinoLocation(models.Model):
  title = models.CharField('Название', max_length=60)
  urlMap = models.URLField('Ссылка на карту', max_length=512)

  def __str__(self):
    return self.title

  class Meta:
    verbose_name = 'Местоположение кино'
    verbose_name_plural = 'Местоположения кино'


class Films(models.Model):

  status_film = (
    ('poster', 'В афише'),
    ('no_poster', 'Не в афише'),
    ('no_poster_system', 'Убран системой из афиши'),
  )

  image = models.ImageField('Постер', upload_to="img/")
  title = models.CharField('Название фильма', max_length=60)
  video = EmbedVideoField('Трейлер')
  date = models.DateTimeField('Начало сеанса')
  genre = models.CharField('Жанр', max_length=16)
  price = models.DecimalField('Цена', max_digits= 5, decimal_places=2, default=0)
  describe = models.TextField('Описание')
  loc = models.ForeignKey('KinoLocation', on_delete=models.SET_NULL, null=True)
  sum_tickets = models.IntegerField('Количество билетов к продаже', default=0)
  status = models.CharField('Статус', choices=status_film, max_length=32, default='poster')

  def __str__(self):
      return self.title

  class Meta:
    verbose_name = 'Фильм'
    verbose_name_plural = 'Фильмы'

class FAQ(models.Model):
    question = models.TextField('Вопрос')
    answer = models.TextField('Ответ')

    def __str__(self):
      return self.question

    class Meta:
      verbose_name = 'FAQ'
      verbose_name_plural = 'FAQ'

class purchased_tickets_status(auto):
  NONE = 'none'
  WAIT_PAYMENT = 'wait_payment'#ожидание платежа
  PAID = 'paid' #оплачено
  NOT_VALID = 'not_valid' #недействительно

class PurchasedTickets(models.Model):

  status_choices = (
    ('none', 'none'),
    ('wait_payment', 'Ожидает оплаты'),
    ('paid', 'Оплачен'),
    ('not_valid', 'Недействителен'),
  )

  payment_number = models.BigIntegerField('Номер платежа', default=0)
  date_created = models.DateTimeField('Дата создания', auto_now_add=True)
  date_session = models.DateTimeField('Дата сеанса')
  number_telephone = models.CharField('Номер телефона', max_length=24)
  number_car = models.CharField('Номер машины', max_length=10)
  status = models.CharField('Статус', max_length=32, choices=status_choices, default=purchased_tickets_status.NONE)
  film = models.ForeignKey('Films', on_delete=models.SET_NULL, null=True)

  def __str__(self):
    return self.number_telephone + ' ' + self.number_car

  class Meta:
    verbose_name = 'Купленный билет'
    verbose_name_plural = 'Купленные билеты'

"""class Task(models.Model):
  time = models.DateTimeField('Время через которое нужно исполнить')
  complete = models.BooleanField('Статус исполнения', default=False)"""