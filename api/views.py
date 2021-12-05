from django.utils import timezone
from django.contrib.auth import authenticate, login

from rest_framework import viewsets
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend

from mainapp.models import Words, GeneralWordsStat, WordStat, WordDatesStat, User
from mainapp.learn_algorithm import WordOps

from .mixins import WordsListMixin, PaginationPermissionMixin
from .permissions import AdminOrReadonlyPermission
from .serializers import (
    GeneralStatSerializer,
    WordsStatsSerializer,
    WordDatesStatSerializer,
    GetNextWordSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer
)
from .utils import GeneralStatFilter, WordDatesFilter, get_word_tenses, WordStat


class AllWordsViewSet(WordsListMixin, viewsets.ModelViewSet):
    """Вывод всех слов"""

    permission_classes = [AdminOrReadonlyPermission]
    queryset = Words.objects.filter(author__isnull=True)


class OwnWordsViewSet(WordsListMixin, viewsets.ModelViewSet):
    """Вывод личных слов"""

    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        return Words.objects.filter(author=self.request.user)


class WordsStatsAPIView(PaginationPermissionMixin, ListAPIView):
    """Вывод статистики слов пользователя"""

    serializer_class = WordsStatsSerializer

    def get_queryset(self):
        return Words.objects.filter(stat__user=self.request.user)


class WordStatAPIView(RetrieveAPIView):
    """Вывод статистики слова"""

    serializer_class = WordsStatsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Words.objects.filter(stat__isnull=False, stat__user=self.request.user)

class GeneralStatAPIView(PaginationPermissionMixin, ListAPIView):
    """Вывод общей статистики пользователя"""

    serializer_class = GeneralStatSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = GeneralStatFilter

    def get_queryset(self):
        return GeneralWordsStat.objects.filter(user=self.request.user)


class WordDatesStatAPIView(PaginationPermissionMixin, ListAPIView):
    """Вывод статистики пользователя по датам"""

    serializer_class = WordDatesStatSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WordDatesFilter

    def get_queryset(self):
        return WordDatesStat.objects.filter(
            word_stat__word=self.kwargs.get('pk'),
            word_stat__user=self.request.user
        )


class GetNextWordAPIView(APIView):
    """Получение следущего слова пользователя"""

    permission_classes = [IsAuthenticated]
    operation = WordOps()

    def get(self, request):

        word = self.operation.get_word(request)
        if not word:
            return Response({'code': "No words"}, status=404)

        tenses = get_word_tenses(word)
        stat = word.stat.filter(user=request.user).first()
        word_dates_stat = WordDatesStat.objects.filter(word_stat=stat)
        stat_today = GeneralWordsStat.objects.get_or_create(user=request.user, date=timezone.now())[0]
        all_stat = WordStat(
            word=word,
            tenses=tenses,
            stat=stat,
            word_dates_stat=word_dates_stat,
            stat_today=stat_today
        )
        serializer = GetNextWordSerializer(all_stat)

        return Response(serializer.data)

    def post(self, request):
        self.operation.create_or_edit_word_stat(
            request,
            request.POST.get('word_id'),
            request.POST.get('is_correct')
        )
        return Response({'success': 'Success!'}, status=200)


class CreateUserAPIView(APIView):
    """Регистрация пользователя"""

    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'Успешно': 'Пользователь успешно создан'}, status=200)


class LoginAPIView(APIView):
    """Вход"""

    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)
        if not user:
            return Response({'Ошибка': 'Не удалось найти пользователя'}, status=400)

        login(request, user)

        return Response({'Успешно': 'Вход успешно выполнен'}, status=200)


class JWTTestView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(status=200)