from django.contrib import messages
from django.core import serializers
from django.db.models import Q
from django.db.models.functions import Length
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.views.generic.base import View
from django.middleware.csrf import get_token
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from pattern import en
from django.forms.models import model_to_dict
import json
from django.core.serializers.json import DjangoJSONEncoder
from slugify import slugify

from .forms import UserRegisterForm
from .learn_algorithm import *
from .models import *
from .utils import CustomErrorList
from .utils import GetWordsMixin, AddEditWordMixin
import functools

def index(request):
    """Главная страница сайта"""

    return render(request, 'mainapp/main_page.html')


class WordsView(GetWordsMixin, ListView):
    """Просмотр списка слов"""

    pass


class AddWordsView(AddEditWordMixin, CreateView):
    """Добавление личных слов"""

    template_name = 'mainapp/add_words.html'

    def form_valid(self, form, *args, **kwargs):
        return super(AddWordsView, self).form_valid(form, 'добавлено')

    def form_invalid(self, form, *args, **kwargs):
        return super(AddWordsView, self).form_invalid(form, 'добавления')


class WordsUpdateView(AddEditWordMixin, UpdateView):
    """Изменение своих слов"""

    template_name = 'mainapp/edit_words.html'

    def get_form(self, form_class=None):
        return self.form_class(**self.get_form_kwargs(), user=self.request.user, validate_word_and_slug=False,
                               error_class=CustomErrorList)

    def get_object(self, queryset=None):
        slug_ = self.kwargs.get('word_slug')
        return get_object_or_404(Words, slug=slug_)

    def form_valid(self, form, *args, **kwargs):
        return super(WordsUpdateView, self).form_valid(form, msg='изменено')

    def form_invalid(self, form, *args, **kwargs):
        return super(WordsUpdateView, self).form_invalid(form, msg='изменения')


class WordDeleteView(DeleteView):
    """Удаление своих слов"""

    model = Words

    def get_success_url(self):
        return f"{reverse('words')}?words=own_words"

    def get_object(self, queryset=None):
        id = self.kwargs.get('word_id')
        return get_object_or_404(Words, id=id)

    def delete(self, request, *args, **kwargs):
        object = self.get_object()
        messages.error(request, f'Слово {object.word} удалено')
        return super(WordDeleteView, self).delete(self, request, *args, **kwargs)

def add_to_own_words(request, word_id):
    """Добавление слова к своим из списка"""

    word = get_object_or_404(Words, id=word_id)
    word.pk = None
    word.author = request.user
    word.slug = slugify(f'{word.word}-{word.translation}-{request.user}')
    word.save()
    messages.success(request, f'Слово {word.word} добавлено')
    return redirect(request.META.get('HTTP_REFERER'))


def register(request):
    """Регистрация"""

    if request.method == 'POST':
        form = UserRegisterForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вы успешно зарегистрировались')
            return redirect('login')
        else:
            messages.error(request, 'Ошибка регистрации')
    else:
        form = UserRegisterForm()
    return render(request, 'mainapp/registration.html', {'form': form})


class SearchWordsView(View):
    """ Живой поиск слов"""

    def get(self, request):
        csrf_token = get_token(request)
        query = request.GET.get('word', '').lower()
        words_type = request.GET.get('words_type', '')
        words = Words.objects.filter(
            Q(word__icontains=query) | Q(translation__icontains=query)
        ).order_by(Length('word'), Length('translation'))
        author_filter = dict(author=None)
        if words_type == 'own_words':
            author_filter['author'] = request.user
        words = words.filter(**author_filter)
        if words:
            res = render_to_string('mainapp/seacrh_field.html', {
                'search_words': words[:6],
                'request': request,
                'csrf_token': csrf_token
            })
            return JsonResponse(res, safe=False)
        return JsonResponse("Ничего не найдено", status=204, safe=False)


def learning(request):
    """Изучение слов"""

    words_type = request.GET.get('words')
    is_words_exist = True
    if words_type == 'own_words':
        is_words_exist = Words.objects.filter(author=request.user).count() > 0
    return render(request, 'mainapp/learning.html', {'is_words_exist': is_words_exist})


class ReturnNewWordInInputView(View):
    """Возвращение слова с помощью алгоритма подбора"""

    operation = WordOps()

    def get(self, request):
        word = self.operation.get_word(request)
        word_lst = word.word.split()

        tenses = [item for sublist in [en.lexeme(i) for i in word_lst] for item in sublist]  # pluralization, comparative, superlative
        tenses += [item for sublist in
                   [[en.pluralize(i), en.comparative(i), en.superlative(i)] for i in
                    word_lst] for item in
                   sublist]

        stat = word.stat.filter(user=request.user).first()
        word_dates_stat = list(WordDatesStat.objects.filter(word_stat=stat).values())
        stat_today = GeneralWordsStat.objects.get_or_create(user=request.user, date=timezone.now())[0]
        data = {'data': model_to_dict(word, fields=['word', 'translation', 'rusex', 'engex', 'id']),
                'tenses': tenses,
                'stat': model_to_dict(stat) if stat else None,
                'word_dates_stat': word_dates_stat,
                "stat_today": model_to_dict(stat_today)
                }
        return JsonResponse(data)

    def post(self, request):
        self.operation.create_or_edit_word_stat(request,
                                                request.POST.get('word_id'),
                                                request.POST.get('is_correct'))
        return JsonResponse({'success': 'Success!'}, status=200)

class GetStatView(View):
    """Возвращение статистики слова"""

    def get(self, request):
        word_id = int(request.GET.get('word_id'))
        word = Words.objects.get(pk=word_id)
        stat = word.stat.filter(user=request.user).first()
        word_dates_stat = list(WordDatesStat.objects.filter(word_stat=stat).values())
        word_stat = {
            'stat': model_to_dict(stat) if stat else None,
            'word_dates_stat': word_dates_stat
        }

        return JsonResponse(word_stat)


class GeneralStatView(View):
    """Возвращение общей статистики по словам"""

    def get(self, request):
        general_stat = list(GeneralWordsStat.objects.filter(user=request.user).values())
        return render(request, 'mainapp/general_stat.html', {'general_stat': json.dumps(general_stat, cls=DjangoJSONEncoder)})