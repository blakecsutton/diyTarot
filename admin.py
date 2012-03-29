from django.contrib import admin
from models import Deck, Suit
from models import MajorArcana, MinorArcana
from models import MeaningSet, Meaning
from models import Spread, CardPosition 

class MajorArcanaAdmin(admin.ModelAdmin):
    fields = ('tarot_index', 'deck', 'title', 'image', 'caption', 'description')
    list_display = ('tarot_index', 'title', 'caption', 'deck')
    list_filter = ['deck', 'tarot_index']
    search_fields = ['title', 'caption', 'description']

class MinorArcanaAdmin(admin.ModelAdmin):
    fields = ('tarot_index', 'deck', 'suit', 'rank', 'title', 'image', 'caption', 'description')
    list_display = ('tarot_index', 'title', 'rank', 'suit', 'caption', 'deck')
    list_filter = ['deck', 'rank']
    search_fields = ['suit__suit', 'suit__name', 'title', 'caption', 'description']
    
class SuitInline(admin.TabularInline):
    model = Suit
    extra = 4

class DeckAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'meaning_set', 'description')
    list_filter = ['meaning_set']
    inlines = [SuitInline]
    
class MeaningSetAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'description')
    
class MeaningAdmin(admin.ModelAdmin):
    model = Meaning
    list_display = ('meaning_set', 'tarot_index', 'keywords', 'predictions', 
                    'reversed_keywords', 'reversed_predictions')
    list_filter = ['meaning_set', 'tarot_index']
    search_fields = ['keywords', 'predictions', 
                    'reversed_keywords', 'reversed_predictions']
  
class CardPositionInline(admin.TabularInline):
    model = CardPosition
    list_display = ('index', 'title', 'x_coordinate', 'y_coordinate', 'spread')
    extra = 3
    
class SpreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'source', 'description')
    inlines = [CardPositionInline]
    
# Register this admin so it appears on the main admin page as an app that
# can be administrated.
admin.site.register(MajorArcana, MajorArcanaAdmin)
admin.site.register(MinorArcana, MinorArcanaAdmin)
admin.site.register(Deck, DeckAdmin)
admin.site.register(MeaningSet, MeaningSetAdmin)
admin.site.register(Meaning, MeaningAdmin)
admin.site.register(Spread, SpreadAdmin)