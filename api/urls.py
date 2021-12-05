from rest_framework import routers

from django.urls import path

from .views import (
    AllWordsViewSet,
    OwnWordsViewSet,
    GeneralStatAPIView,
    WordsStatsAPIView,
    WordStatAPIView,
    WordDatesStatAPIView,
    GetNextWordAPIView,
    CreateUserAPIView,
    LoginAPIView,
    JWTTestView
)


router = routers.SimpleRouter()
router.register('words', AllWordsViewSet, basename='words_all_words_api')
router.register('own_words', OwnWordsViewSet, basename='words_own_words_api')

urlpatterns = [
    path('words_stats/', WordsStatsAPIView.as_view(), name='words_stats_api'),
    path('word_stat/<int:pk>/', WordStatAPIView.as_view(), name='word_stat_api'),
    path('general_stat/', GeneralStatAPIView.as_view(), name='general_stat_api'),
    path('word_dates_stat/<int:pk>/', WordDatesStatAPIView.as_view(), name='word_dates_stat_api'),
    path('get_next_word/', GetNextWordAPIView.as_view(), name='get_next_word_api'),
    path('create_user/', CreateUserAPIView.as_view(), name='create_user_api'),
    path('test/', JWTTestView.as_view(), name='test_api'),
    path('login/', LoginAPIView.as_view(), name='login_api')
]

urlpatterns += router.urls