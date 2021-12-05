from django.urls import path, include
from .views import *
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView

urlpatterns = [
    path('', TemplateView.as_view(template_name='mainapp/main_page.html'), name='index'),
    path('login/', LoginView.as_view(template_name="mainapp/login.html"), name='login'),
    path('registration/', RegistrationView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(template_name="mainapp/registration.html"), name='logout'),
    path('words/', WordsView.as_view(), name='words'),
    path('words/add_words/', AddWordsView.as_view(), name='add_words'),
    path('words/update_words/<int:word_id>/', WordsUpdateView.as_view(), name='update_words'),
    path('words/delete_word/<int:word_id>/', WordDeleteView.as_view(), name='delete_word'),
    path('words/add_to_own_words/<int:word_id>/', AddToOwnWordsView.as_view(), name='add_to_own_words'),
    path('words/search_words/', SearchWordsView.as_view(), name='search_words'),
    path('words/learning/', LearningView.as_view(), name='learning'),
    path('words/word_stat/<int:pk>/',
         DetailView.as_view(
                model=Words,
                template_name="mainapp/word_stat.html",
                context_object_name='word',
            ),
         name='word_stat'),
    path('stat/', TemplateView.as_view(template_name='mainapp/general_stat.html'), name='general_stat'),
]