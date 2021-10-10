from .models import Words, WordStat, GeneralWordsStat, WordDatesStat
from django.db.models.aggregates import Count

from random import randint

from datetime import timedelta
from django.utils import timezone

from django.db.models import F


class WordOps:
    def __init__(self):
        self.all_words = Words.objects.all()

    def get_random_word(self, words):
        """Возвращает случайное слово"""

        item_count = words.aggregate(count=Count('id'))['count']
        if not item_count:
            return
        random_word = words[randint(1, item_count) - 1]
        return random_word

    def get_word(self, request):
        words_type = request.GET.get('words')
        author_filter = dict(author=None)
        if words_type == 'own_words':
            author_filter['author'] = request.user
        words = self.all_words.filter(**author_filter)
        # Выборка слов по статистике. Если ее нет - выбирается рандомное слово
        words_with_stat = words.filter(stat__user=request.user)
        if not words_with_stat:
            return self.get_random_word(words)
        # Возвращает подходящее по времени изучения слово
        appropriate_words = words_with_stat.filter(stat__next_review__lte=timezone.now(),
                                                   stat__gap_after_right_answer__lte=timezone.now(),
                                                   stat__is_learned=False)
        if not appropriate_words:
            # Если подходящего слова нет - возращает слово без статистики
            new_word = self.get_random_word(words.filter(stat__user__isnull=True))
            if new_word:
                return new_word
            not_learned_words = self.get_random_word(words.filter(stat__is_learned=False))
            # Иначе - случайное слово
            if not_learned_words:
                return not_learned_words
            return self.get_random_word(words)
        return appropriate_words.first()

    def create_or_edit_word_stat(self, req, word_pk, is_correct):
        is_correct = False if is_correct == 'false' else True

        def edit_stat_for_word(is_correct):
            """Изменение статистики изучения слова"""

            REVIEW_TIME = {k: v for k, v in zip(range(1, 7), (2, 5, 8, 9, 10, 10))}
            MEMORISE_COEF = {k: v for k, v in zip(range(6), (3, 3, 2, 2, 2, 1))}
            stat = word_stat.first()
            dates_stat = WordDatesStat.objects.get_or_create(word_stat=stat, date=timezone.now())[0]
            all_words_stat = GeneralWordsStat.objects.get_or_create(user=req.user, date=timezone.now())[0]

            # Если слово не подходит по времени, то статистика не учитывается
            if stat.next_review > timezone.now() or stat.is_learned:
                if is_correct:
                    stat.correct_answers += 1
                    stat.correct_answers_in_a_row += 1
                    dates_stat.correct_answers += 1
                    all_words_stat.correct_answers += 1
                else:
                    stat.incorrect_answers += 1
                    stat.correct_answers_in_a_row = 0
                    all_words_stat.incorrect_answers += 1
                    dates_stat.incorrect_answers += 1

                stat.is_active_stat = False
                all_words_stat.all_words += 1
                all_words_stat.save()
                stat.save()
                dates_stat.save()
                return

            stat.is_active_stat = True

            memorise_coefficient = stat.memorise_coefficient
            memorise_lvl = stat.memorise_lvl

            if is_correct:
                # Если уровень слова достиг 6, то это слово можно считать выученым
                if stat.memorise_lvl == 6:
                    stat.is_learned = True
                    all_words_stat.learned_words += 1
                    stat.save()
                    all_words_stat.save()
                    return
                if stat.skip_lvl_flag:
                    # Если слово угадано с 1 попытки, то можно пропустить 1 уровень
                    stat.memorise_lvl += 1
                else:
                    stat.memorise_coefficient += 1
                stat.correct_answers += 1
                all_words_stat.all_words += 1
                all_words_stat.correct_answers += 1
                dates_stat.correct_answers += 1
                stat.correct_answers_in_a_row += 1
            else:
                stat.skip_lvl_flag = False
                stat.incorrect_answers += 1
                all_words_stat.incorrect_answers += 1
                all_words_stat.all_words += 1
                dates_stat.incorrect_answers += 1
                stat.correct_answers_in_a_row = 0

            if memorise_coefficient >= MEMORISE_COEF.get(memorise_lvl):
                stat.skip_lvl_flag = True
                stat.memorise_coefficient = 0
                stat.next_review = timezone.now() + timedelta(days=REVIEW_TIME.get(memorise_lvl))
                stat.memorise_lvl += 1

            dates_stat.save()
            all_words_stat.save()
            stat.save()

        def create_new_stat_for_word(is_correct):
            """Создание статистики слова, если ее еще нет"""

            stat = WordStat(user=req.user)
            stat.save()
            dates_stat = WordDatesStat.objects.create(word_stat=stat, date=timezone.now())
            all_words_stat = GeneralWordsStat.objects.get_or_create(user=req.user, date=timezone.now())[0]
            all_words_stat.new_words += 1
            if is_correct:
                stat.memorise_lvl = 4
                stat.skip_lvl_flag = True
                stat.next_review = timezone.now() + timedelta(days=15)
                stat.correct_answers += 1
                stat.correct_answers_in_a_row += 1
                all_words_stat.correct_answers += 1
                dates_stat.correct_answers += 1
            else:
                stat.incorrect_answers += 1
                all_words_stat.incorrect_answers += 1
                dates_stat.incorrect_answers += 1
            # Сохранение статистики
            stat.save()
            all_words_stat.all_words += 1
            all_words_stat.save()
            dates_stat.save()
            word.stat.add(stat)

        word = Words.objects.get(pk=word_pk)
        word_stat = word.stat.filter(user=req.user)

        if not word_stat.exists() and (is_correct or not is_correct):
            create_new_stat_for_word(is_correct)
        else:
            edit_stat_for_word(is_correct)
