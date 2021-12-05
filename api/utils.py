from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
from django.utils.timezone import now

from mainapp.models import GeneralWordsStat, WordDatesStat

from datetime import timedelta
from pattern import en

class SmallPagesPagination(PageNumberPagination):
    page_size = 40


class GeneralStatFilter(filters.FilterSet):
    """Фильтр вывода общей статистики"""

    filter = {
        'last_30_days': lambda qs, name: qs.filter(**{
            '%s__year' % name: now().year,
            '%s__gte' % name: now()-timedelta(days=30)
        })
    }

    choice = [
        ('last_30_days', 'Последние 30 дней')
    ]

    custom_filters = dict(**filters.DateRangeFilter.filters, **filter)
    custom_choices = filters.DateRangeFilter.choices + choice

    date = filters.DateRangeFilter(filters=custom_filters, choices=custom_choices)

    class Meta:
        model = GeneralWordsStat
        fields = ['date']


class WordDatesFilter(filters.FilterSet):
    """Фильтр для вывода статистики по датам"""

    date = filters.DateRangeFilter()

    class Meta:
        model = WordDatesStat
        fields = ['date']


class WordStat:
    def __init__(self, word, tenses, stat, word_dates_stat, stat_today):
        self.word = word
        self.tenses = tenses
        self.stat = stat
        self.word_dates_stat = word_dates_stat
        self.stat_today = stat_today


def get_word_tenses(word):
    """Получение всех форм слова"""

    words = word.word.split()
    tenses = [item for sublist in [en.lexeme(i) for i in words] for item in
              sublist]
    tenses += [item for sublist in
               [[en.pluralize(i), en.comparative(i), en.superlative(i)] for i in
                words] for item in
               sublist]
    return tenses