from django import template
from django.conf import settings
from mainapp.models import Words
register = template.Library()


@register.filter(name='getattr')
def getattr_(value, arg):
    """Возвращает label обьекта"""

    return value.fields[arg].label if hasattr(value.fields[arg], 'label') else settings.TEMPLATE_STRING_IF_INVALID


@register.filter(name='is_own_word')
def is_own_word(value, user):
    """Проверка принадлежит ли это слово пользователю или это общее слово"""

    return Words.objects.filter(
        word=value.word,
        translation=value.translation,
        author=user
    ).exists()


@register.filter(name='has_stat')
def has_stat(word, user):
    """Проверка если ли у слова статистика"""

    return word.stat.filter(user=user).count()


