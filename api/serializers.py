from rest_framework import serializers
from mainapp.models import Words, GeneralWordsStat, WordStat, WordDatesStat, User
from django.db.models import Q

class WordsSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Words
        fields = ['id', 'word', 'translation', 'engex', 'rusex', 'author']


class StatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = WordStat
        fields = ['pk', 'correct_answers', 'incorrect_answers',
                  'correct_answers_in_a_row', 'memorise_lvl', 'memorise_coefficient',
                  'gap_after_right_answer', 'skip_lvl_flag', 'next_review', 'last_attempt',
                  'is_learned', 'is_active_stat', 'created_at']


class WordsStatsSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(slug_field='username', read_only=True)
    stat = StatsSerializer(many=True)

    class Meta:
        model = Words
        fields = ['word', 'author', 'stat']


class GeneralStatSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = GeneralWordsStat
        fields = ['user', 'date', 'correct_answers', 'incorrect_answers', 'new_words', 'learned_words', 'all_words']


class WordDatesStatSerializer(serializers.ModelSerializer):

    class Meta:
        model = WordDatesStat
        fields = ['date', 'correct_answers', 'incorrect_answers']


class GetNextWordSerializer(serializers.Serializer):

    word = WordsSerializer()
    tenses = serializers.ListField()
    stat = StatsSerializer()
    word_dates_stat = WordDatesStatSerializer(many=True)
    stat_today = GeneralStatSerializer()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserRegistrationSerializer(serializers.Serializer):

    username = serializers.CharField(min_length=8, max_length=100, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=8, max_length=100, required=True)
    password2 = serializers.CharField(min_length=8, max_length=100, required=True)

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')

        if not password == password2:
            raise serializers.ValidationError('Пароли не совпадают')

        return data

    def create(self, validated_data):

        validated_data.pop('password2')
        password = validated_data.get('password')
        if User.objects.filter(username=validated_data.get('username')).exists():
            raise serializers.ValidationError({'username': ['Такой пользователь уже существует']})
        elif User.objects.filter(email=validated_data.get('email')).exists():
            raise serializers.ValidationError({'email': ['Пользователь с таким email уже существует']})

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):

    username = serializers.CharField(min_length=8, max_length=100, required=True)
    password = serializers.CharField(min_length=8, max_length=100, required=True)
