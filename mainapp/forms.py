from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import ValidationError
from slugify import slugify
from .views import *
from common.middleware import get_current_user
from django.core import validators
from django.contrib.auth.models import User
from .models import *


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(max_length=20,
                               min_length=4,
                               label='Имя пользователя',
                               validators=[validators.RegexValidator(regex='^[a-zA-Z0-9_!@#$%^&*]*$',
                                                                     message='Вы можете использовать только '
                                                                             'латинские буквы и цифры '
                                                                             'а также некоторые символы',
                                                                     code='invalid_username')],
                               widget=forms.TextInput(attrs={
                                'class': 'form-input',
                                'id': 'txt-input2',
                                'placeholder': "Имя пользователя"}))
    email = forms.EmailField(max_length=100,
                             min_length=4,
                             label='Email',
                             widget=forms.EmailInput(attrs={
                                'class': 'form-input',
                                'id': 'txt-input',
                                'placeholder': "Email"
                             }))
    password1 = forms.CharField(
                                min_length=8,
                                label='Пароль',
                                widget=forms.PasswordInput(attrs={
                                    'class': 'form-input',
                                    'id': 'pwd',
                                    'placeholder': "Пароль",
                                }))
    password2 = forms.CharField(
                                min_length=8,
                                label = 'Подтверждение пароля',
                                widget=forms.PasswordInput(attrs={
                                    'class': 'form-input',
                                    'id': 'pwd2',
                                    'placeholder': "Повторите пароль",
                                }))

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Такой email уже зарегистрирован, введите другой')
        return email

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class AddEditWordForm(forms.ModelForm):
    def __init__(self, user=None, validate_word_and_slug=True, *args, **kwargs):
        if user is not None:
            self.user = user
        self.validate = validate_word_and_slug  # Проверка слага на уникальность
        super().__init__(*args, **kwargs)

    def clean(self):
        slug = slugify(f'{self.cleaned_data["word"]}-{self.cleaned_data["translation"]}-{self.user}')

        if Words.objects.filter(slug=slug).exists() and self.validate:
            raise ValidationError('Похоже, данное слово и перевод уже существует, введите другое слово.')
        self.cleaned_data['slug'] = slug
        super(AddEditWordForm, self).clean()

    class Meta:
        model = Words
        fields = ('word', 'translation', 'engex', 'rusex')
        labels = {'word': 'Слово', 'translation': "Перевод", 'engex': "Пример предложения (англ)",
                  'rusex': "Пример предложения (русс)"}
        widgets = {
            'word': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Только латинница"}),
            'translation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Только кириллица"}),
            'engex': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Только латинница"}),
            'rusex': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Только кириллица"}),
        }
