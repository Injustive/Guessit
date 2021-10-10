from .models import *
from .forms import AddEditWordForm
from django.contrib import messages
from django.forms.utils import ErrorList


class CustomErrorList(ErrorList):
    """Редактирование списка ошибок до более понятного вида"""

    def __str__(self):
        return '\n'.join(error for error in self)


class GetWordsMixin:
    """Миксин возвращения списка слов (личных или общих)"""

    model = Words
    context_object_name = 'words'
    template_name = 'mainapp/words.html'
    paginate_by = 25

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        words_set = super(GetWordsMixin, self).get_queryset()
        if self.request.GET.get('words') == 'own_words':
            return words_set.filter(author=self.request.user)
        return words_set.filter(author=None)

class AddEditWordMixin:
    """Редадктирование или добавление личных слов"""

    form_class = AddEditWordForm

    def get_form(self, form_class=None):
        return self.form_class(**self.get_form_kwargs(), user=self.request.user, error_class=CustomErrorList)

    def get_success_url(self):
        return f"{reverse('words')}?words=own_words"

    def form_valid(self, form, msg):
        instance = form.save(commit=False)
        instance.slug = form.cleaned_data['slug']
        instance.author = self.request.user
        instance.save()
        messages.success(self.request, f"Слово '{form.cleaned_data['word'].title()}' успешно {msg}")
        return super().form_valid(instance)

    def form_invalid(self, form, msg):
        messages.error(self.request, f"Ошибка {msg}")
        return super().form_invalid(form)
