from django.contrib import admin
from .models import *

class WordsAdmin(admin.ModelAdmin):
    list_display = ('id', 'word', 'translation', 'engex', 'rusex', 'author', 'slug')
    list_display_links = ('word', 'author')
    search_fields = ('word', 'translation', 'engex', 'rusex')


admin.site.register(Words, WordsAdmin)
admin.site.register(WordStat)
admin.site.register(GeneralWordsStat)
admin.site.register(WordDatesStat)