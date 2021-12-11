from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Length
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.views.generic.base import View
from django.middleware.csrf import get_token
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import UserRegisterForm
from .models import *
from .utils import CustomErrorList
from .utils import GetWordsMixin, AddEditWordMixin

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
        return self.form_class(**self.get_form_kwargs(), error_class=CustomErrorList)

    def get_object(self, queryset=None):
        word_id = self.kwargs.get('word_id')
        return get_object_or_404(Words, pk=word_id)

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


class AddToOwnWordsView(View):
    """Добавление слова к своим из списка"""

    def get(self, request, word_id):
        word = get_object_or_404(Words, id=word_id)
        word.pk = None
        word.author = request.user
        word.save()
        messages.success(request, f'Слово {word.word} добавлено')
        return redirect(request.META.get('HTTP_REFERER'))


class RegistrationView(View):
    """Регистрация"""

    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'mainapp/registration.html', {'form': form})
    
    def post(self, request):
        form = UserRegisterForm(request.POST, error_class=CustomErrorList)
            if form.is_valid():
                form.save()
                messages.success(request, 'Вы успешно зарегистрировались')
                return redirect('login')
            else:
                messages.error(request, 'Ошибка регистрации')


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


class LearningView(View):
    """Изучение слов"""

    def get(self, request):
        words_type = request.GET.get('words')
        is_words_exist = True
        if words_type == 'own_words':
            is_words_exist = Words.objects.filter(author=request.user).count() > 0
        return render(request, 'mainapp/learning.html', {'is_words_exist': is_words_exist})



