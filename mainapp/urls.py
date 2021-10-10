from django.urls import path, include
from .views import *
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('', index, name='index'),
    path('login/', LoginView.as_view(template_name="mainapp/login.html"), name='login'),
    path('registration/', register, name='register'),
    path('logout/', LogoutView.as_view(template_name="mainapp/registration.html"), name='logout'),
    path('words/', WordsView.as_view(), name='words'),
    path('words/add_words/', AddWordsView.as_view(), name='add_words'),
    path('words/update_words/<slug:word_slug>', WordsUpdateView.as_view(), name='update_words'),
    path('words/delete_word/<int:word_id>', WordDeleteView.as_view(), name='delete_word'),
    path('words/add_to_own_words/<int:word_id>', add_to_own_words, name='add_to_own_words'),
    path('words/search_words', SearchWordsView.as_view(), name='search_words'),
    path('words/learning/', learning, name='learning'),
    path('words/get_stat/', GetStatView.as_view(), name='get_stat'),
    path('words/learning/return_new_word_in_input/', ReturnNewWordInInputView.as_view(), name='return_new_word_in_input'),
    path('stat/', GeneralStatView.as_view(), name='general_stat'),
]