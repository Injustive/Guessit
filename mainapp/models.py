from django.db import models
from django.shortcuts import reverse
from django.core import validators
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
User = get_user_model()


def get_gap_after_answer():
    return timezone.now()+timedelta(minutes=3)


class Words(models.Model):
    word = models.CharField(max_length=100, verbose_name='Слово', validators=[validators.RegexValidator(
        regex=r'[а-яА-ЯёЁ]', inverse_match=True, message='Введите слово латиницей!')])
    translation = models.CharField(max_length=100, verbose_name='Перевод', validators=[validators.RegexValidator(
        regex=r'[а-яА-ЯёЁ]', message='Введите перевод латиницей!')])
    engex = models.CharField(max_length=300, verbose_name="Пример англ.", validators=[validators.RegexValidator(
        regex=r'[а-яА-ЯёЁ]', inverse_match=True, message='Введите пример латиницей!!')])
    rusex = models.CharField(max_length=300, verbose_name="Пример русс.", validators=[validators.RegexValidator(
        regex=r'[а-яА-ЯёЁ]', message='Введите пример кирилицей!')])
    photoURL = models.URLField(max_length=1000, verbose_name="Ссылка на миниатюру", blank=True, null=True)
    stat = models.ManyToManyField('WordStat', related_name='word')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор", blank=True, null=True)

    def __str__(self):
        return f'{self.word}---{self.translation}'

    class Meta:
        verbose_name = 'Слово'
        verbose_name_plural = 'Слова'
        ordering = ('word',)


class WordStat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    correct_answers = models.IntegerField(default=0, verbose_name="Правильные ответы")
    incorrect_answers = models.IntegerField(default=0, verbose_name="Неправильные ответы")
    correct_answers_in_a_row = models.IntegerField(default=0, verbose_name='Правильных ответов подряд')
    memorise_lvl = models.IntegerField(default=1, verbose_name="Уровень запоминания")  # Max - 6
    memorise_coefficient = models.IntegerField(default=0, verbose_name="Коеф. запоминания")  # Max-3, потом 3, 3, 2, 2,1
    gap_after_right_answer = models.DateTimeField(default=get_gap_after_answer,
                                                  verbose_name='Время после правильного ответа')
    skip_lvl_flag = models.BooleanField(default=False, verbose_name='Пропуск уровня')
    next_review = models.DateTimeField(default=timezone.now, verbose_name="Следующее повторение")  # 2, 5, 8, 15, 30, 40
    last_attempt = models.DateTimeField(verbose_name="Последнее сохранение", auto_now=True)
    is_learned = models.BooleanField(default=False, verbose_name='Выучено?')
    is_active_stat = models.BooleanField(default=True, verbose_name='Учитывание статистики')
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Время создания")
    
    def save(self, *args, **kwargs):
        self.gap_after_right_answer = timezone.now() + timedelta(minutes=3)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user}-{self.memorise_lvl}-{"Выучено" if self.is_learned else "Невыучено"}'

    class Meta:
        verbose_name = 'Статистика слова'
        verbose_name_plural = 'Статистика слов'
        ordering = ('next_review',)

class WordDatesStat(models.Model):
    word_stat = models.ForeignKey(WordStat, on_delete=models.CASCADE, verbose_name='Статистика слова',
                                  related_name="word_dates_stat", null=True)
    date = models.DateField(verbose_name="Дата", auto_now_add=True)
    correct_answers = models.IntegerField(default=0, verbose_name="Правильные ответы")
    incorrect_answers = models.IntegerField(default=0, verbose_name="Неправильные ответы")

    def __str__(self):
        return f"{self.word_stat}-{self.date}"

    class Meta:
        verbose_name = 'Статистика слова по датам'
        verbose_name_plural = 'Статистика слов по датам'
        ordering = ('-date',)


class GeneralWordsStat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(verbose_name="Дата", auto_now_add=True)
    correct_answers = models.IntegerField(default=0, verbose_name="Правильные ответы")
    incorrect_answers = models.IntegerField(default=0, verbose_name="Неправильные ответы")
    new_words = models.IntegerField(default=0, verbose_name="Новые слова")
    learned_words = models.IntegerField(default=0, verbose_name="Выучено слов")
    all_words = models.IntegerField(default=0, verbose_name="Все слова")

    def __str__(self):
        return str(self.date)

    class Meta:
        verbose_name = 'Статистика всех слов'
        verbose_name_plural = 'Статистика всех слов'
        ordering = ('-date',)
