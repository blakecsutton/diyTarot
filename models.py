import os.path
from django.db import models
import tarot_constants

# MeaningSet class, which groups together a set of related meanings (predictions
# and keywords) so they can be distinguished from other sets. E.g., you might have
# a funny deck and want to give it all funny meanings, but not have those interfere
# with "serious" readings on other decks.
class MeaningSet(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    description = models.TextField()
    
    def __unicode__(self):
        return "%s, by %s" % (self.title, self.author)
 
class Meaning(models.Model):
    """ This is a model to group together all of the meaning information for a single
        card in the context of a single meaning set. It includes meanings for reversals. """
    
    # Link to the overall meanings set
    meaning_set = models.ForeignKey(MeaningSet)
    
    # This serves as a unenforced foreign key across decks by identifying which card out of 
    # the 78 tarot cards this Prediction applies to
    # However is not a real key -- you can enter meanings for cards that aren't in the system.
    tarot_index = models.PositiveSmallIntegerField(choices=tarot_constants.ALL_CARD_CHOICES)
       
    # Predictions should be sentences separated by spaces.
    predictions = models.TextField() 
    
    # Keywords should be a list of lowercase words or phrases separated by commas, with no
    # period on the end.
    keywords = models.TextField()
    
    reversed_predictions = models.TextField()
    reversed_keywords = models.TextField()
                                       

    def __unicode__(self):
        return "Meaning for card %d in set %s" % (self.tarot_index, self.meaning_set)

    
# Deck class, which represents an particular tarot deck, or group of cards.
class Deck(models.Model):
    meaning_set = models.ForeignKey(MeaningSet)
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField()
    
    # Helper function to get a nice list of only the names of the suits
    # associated with a particular deck.
    def get_suit_names(self):
        suits = Suit.objects.all().filter(deck=self.id)
        suit_list = []
        for suit in suits:
            suit_list.append(suit.name)
        return suit_list

    def __unicode__(self):
        return "%s Deck" % (self.name)
    
# Utility function to automatically generate a separate folder for
# each deck, so that images for each deck are grouped together when uploaded.
def get_deck_path(instance, filename):
    return os.path.join('diytarot/decks', str(instance.deck_id), filename)

class Card(models.Model):
    
    # ForeignKey makes the many-to-one association to a deck
    deck = models.ForeignKey(Deck)
    
    title = models.CharField(max_length=200)
    caption = models.CharField(max_length=200)
    description = models.TextField()
    
    tarot_index = models.PositiveSmallIntegerField(
                                    choices=tarot_constants.ALL_CARD_CHOICES)  
    
    # this ImageField uses the get_deck_path function to find the upload directory
    image = models.ImageField(upload_to=get_deck_path) 
    
    def __unicode__(self):
        return "%s Card of deck %s" % (self.title, self.deck)
    
    
    def get_name(self):
        return "%s" % self.title
    
    # Helper function to be called by the template to get the keywords for the card
    def get_keywords(self):
        # Pull out the keywords for this card only
        meanings = Meaning.objects.all().filter(
                                        meaning_set=self.deck.meaning_set, 
                                        tarot_index=self.tarot_index).values('keywords')
                                        
        # @todo refactor all of this code, move it to views where it belongs
        # and update the templates accordingly
        keywords = []
        for meaning in meanings:
            keywords += [meaning['keywords']]
        return keywords
    
    # Helper function to be called by the template to get the reversal keywords for the card
    def get_reversed_keywords(self):
        # Pull out the keywords for this card only
        meanings = Meaning.objects.all().filter(
                                        meaning_set=self.deck.meaning_set, 
                                        tarot_index=self.tarot_index).values('reversed_keywords')                                 
        keywords = []
        for meaning in meanings:
            keywords += [meaning['reversed_keywords']]
        return keywords
                                        
    
    # Helper function to be called by the template to get the reversed predictions for the card
    def get_predictions(self):     
        # Pull out the keywords for this card only
        meanings = Meaning.objects.all().filter(
                                        meaning_set=self.deck.meaning_set_id, 
                                        tarot_index=self.tarot_index).values('predictions')
        predictions = []
        for meaning in meanings:
            predictions += [meaning['predictions']]
        return predictions
    
    # Helper function to be called by the template to get the reversed predictions for the card
    def get_reversed_predictions(self):
        # Pull out the keywords for this card only
        meanings = Meaning.objects.all().filter(
                                        meaning_set=self.deck.meaning_set_id, 
                                        tarot_index=self.tarot_index).values('reversed_predictions')
        predictions = []
        for meaning in meanings:
            predictions += [meaning['reversed_predictions']]
        return predictions
        
# MajorArcana class, which represents Major Arcana cards for various decks.
class MajorArcana(Card):
      
    def get_name(self):
        return self.title
        
    def __unicode__(self):
        return "%s (deck %s)" % (self.title, self.deck)

# Suit class, used to allow different decks to have their own names for the suits,
# while still keeping track of the underlying original suits for comparison.
class Suit(models.Model):
    deck = models.ForeignKey(Deck)
    suit = models.PositiveSmallIntegerField(choices=tarot_constants.SUIT_CHOICES)
    # The name field gives you the option to change the display name
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return "%s" % (self.name)

# MinorArcana class, which represents Minor Arcana cards for various decks.
class MinorArcana(Card):

    suit = models.ForeignKey(Suit)
    rank = models.PositiveSmallIntegerField()
    
    def get_name(self):
        return "%s of %s" % (self.title, self.suit.name)
    
    def __unicode__(self):
        return "%s (suit %s, deck %s)" % (self.title, self.suit, self.deck)

# Spread class, which represents a tarot spread, or card layout.
class Spread(models.Model):
    
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    
    # Optional field allowing link back to original website with the spread
    source = models.TextField(blank=True, default="")
    
    # The description is useful for explaining how to use the spread.
    description = models.TextField()
    
    def __unicode__(self):
        return "%s spread, by %s" % (self.title, self.author)

# CardPosition class, which represents an individual card position in a tarot spread.
class CardPosition(models.Model):
    
    spread = models.ForeignKey(Spread)
    
    # Represents the card position's order in the reading
    index = models.PositiveSmallIntegerField()
    
    # Location for the image in the layout, with axis at top left
    x_coordinate = models.FloatField()
    y_coordinate = models.FloatField()
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    
    
    def __unicode__(self):
        return "%s position, in spread %s" % (self.title, self.spread)