from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.db.models import Q
from functions import *
from models import Deck, Suit, Meaning, MinorArcana, MajorArcana
from models import Spread, CardPosition
from random import choice

def deck_list(request):
    """ This is a view to show a list of all available decks with a few details 
        about each one. We can't use a generic view because we need to cross-reference
        the suits associated with each deck. """
    
    decks = Deck.objects.all()
    
    # Pull the suits for each deck and put them in a tuple with each deck
    deck_list = []
    for deck in decks:
        
        suits = Suit.objects.filter(deck=deck.id)
        deck_list += [ (deck, suits) ]
    
    pages = Paginator(deck_list, 10, 3)
    
    # Check if page is an int, if not deliver page 1
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1 
        
    # Check if page is in range, if not deliver last page
    try:
        result_list = pages.page(page)
    except (EmptyPage, InvalidPage):
        result_list = pages.page( pages.num_pages ) 
        
    context = {'result_list': result_list}

    return render_to_response('diyTarot/deck_list.html', 
                              context_instance=RequestContext(request, context))     
    
def spread_list(request):
    """ This is a view to display the list of spreads. Can't use a generic 
        view because want to cross-reference with the card positions to 
        give information like the number of cards in a spread. """

    # Set up the structures used to add successive filters and handle the query string
    active_options = request.GET.copy()
    query_list = []
    
    # Set up the query objects to search spreads and filter by size
    apply_spread_search_filter(active_options, query_list)
    apply_spread_size_filter(active_options, query_list)
    
    # Annotate each spread with the number of positions associated with it, for sorting
    # and also for filtering by size
    spreads = Spread.objects.annotate(size=Count('cardposition')).filter(*query_list).order_by('size')

    # Paginate the results
    pages = Paginator(spreads, 10, 3)
    current_page = get_current_page(active_options, pages)

    # Temporary, limited tag list before tags are added to the model
    tags = ['daily', 'traditional', 'love', 'work', 'advice', 'choice']        
    tag_results = {}
    for tag in tags:
      tag_query = [Q(title__icontains=tag) | Q(description__icontains=tag)]
      tag_results[tag] = Spread.objects.filter(*tag_query).count()
    
    # Check if there is a default deck stored in the current session
    # This determines which deck to point you to in the links on the spread list, 
    # by remembering your preference in the session.
    if 'deck' in request.session:
        deck = request.session['deck']
    else:
        # @TODO: make the default deck configurable?
        deck = 1
            
    context = {'result_list': current_page,
               'deck': deck,
               'active_options': active_options,
               'tag_results': tag_results}
 
    return render_to_response('diyTarot/spread_list.html',
                              context_instance=RequestContext(request, context))
 
def card_list(request):
    """ This is a view to display all cards in the system, across all decks. Via the 
        GET headers it paginates and filters the resulting list if the various arguments
        exist and are valid in the request. """
    
    # Pull all get parameters from the request into a querydict structure.
    active_options = request.GET.copy()
 
    # Set up the structures used to add successive filters and handle the query string
    filter_args = {}    
    query_list = []
    order_args = []
    
    # Try to apply all possible filters one by one. 
    # If an option's value is not valid it is removed from display_options.
    apply_card_search_filter(active_options, query_list)
    apply_key_filter(active_options, filter_args, 'deck', 'deck')
    apply_card_filter(active_options, filter_args)
    apply_suit_filter(active_options, filter_args)
    apply_rank_filter(active_options, filter_args)
        
    apply_sorting_order(active_options, order_args)
    
    # To search the meanings as well as the Cards, need to get the list of tarot indexes which
    # link to meanings that match the search
    if 'search' in active_options:
        
        meaning_query_list = []
        apply_keyword_search_filter(active_options, meaning_query_list)
        
        # Get all tarot_indexes which have keyword strings containing the search term.
        meanings = Meaning.objects.filter(*meaning_query_list).values('tarot_index', 'meaning_set').order_by('meaning_set')
        
        # Get the id of each card (or set of cards) which matches each tarot_index / meaning_set pair
        # This assures that only the cards that use the matching meaning set get pulled, instead of all cards
        # with a certain tarot index.
        ids = []
        for meaning in meanings:
          ids += Card.objects.filter(tarot_index=meaning['tarot_index'], 
                                    deck__meaning_set=meaning['meaning_set']).values_list('id')                                  
        
        # Reformat list so it can be read directly by the id__in parameter  
        id_list = [card_id[0] for card_id in ids]

        # Pull only the cards that have the same tarot index AND whose deck has the same meaning_set
        query_list[0] |= Q(id__in=id_list)

    # Some of the options only apply to the MinorArcana schema.
    # The rank and suit filters will set the card option automatically.
    if ('cards' in active_options and
        active_options['cards'] =='minors'):
            cards = MinorArcana.objects.filter(*query_list).filter(**filter_args).order_by(*order_args)
    else:
        cards = Card.objects.filter(*query_list).filter(**filter_args).order_by(*order_args)

    # Used by the shared sidebar navigation menu
    base_url = "/diytarot/cards/"
    
    # Populate the deck and suit lists used in navigation
    deck_list = Deck.objects.values('name', 'id')
    suit_list = Suit.objects.filter(deck=deck_list[0]['id']).values('suit', 'name')
    
    # Paginate the queryset and fetch the current page from the URL, with validation
    pages = Paginator(cards, 10, 3)
    current_page = get_current_page(active_options, pages)
    
    context = {'result_list': current_page,
               'base_url': base_url,
               'active_options': active_options,
               'deck_list': deck_list,
               'suit_list': suit_list}

    return render_to_response('diyTarot/card_list.html',
                              context_instance=RequestContext(request, context))   

def deck_detail(request, deck_id):
    """ This is a view to show all the cards associated with a particular 
        tarot deck. """
        
    # Get the list of cards, return the deck listing page if deck doesn't exist.
    try:
        deck = Deck.objects.get(pk=deck_id)
    except Deck.DoesNotExist:
        return deck_list(request)
    
    # Set up the structures used to add successive filters and handle the query string
    active_options = request.GET.copy()
    filter_args = {'deck': deck_id}    
    order_args = []
    
    # Apply the filters one by one. If an option is not valid it is removed from display_options.
    apply_card_filter(active_options, filter_args)
    apply_suit_filter(active_options, filter_args)
    apply_rank_filter(active_options, filter_args)
    apply_sorting_order(active_options, order_args)
    
    # Some of the options only apply to the MinorArcana schema.
    # The rank and suit filters will set the card option automatically.
    if ('cards' in active_options and
        active_options['cards'] =='minors'):
            cards = MinorArcana.objects.filter(**filter_args).order_by(*order_args)
    else:
        cards = Card.objects.filter(**filter_args).order_by(*order_args)

    # The base url, since there is a different one for deck view and all cards view
    base_url = "/diytarot/decks/%s/" % deck_id
    
    # Populate the suit list used in navigation
    suit_list = Suit.objects.filter(deck=deck_id).values('suit', 'name')
    
    # Paginate the queryset and fetch the current page from the URL, with validation
    pages = Paginator(cards, 10, 3)
    current_page = get_current_page(active_options, pages)
    
    context = {'deck': deck,
               'result_list': current_page,
               'base_url': base_url,
               'suit_list': suit_list,
               'active_options': active_options}

    return render_to_response('diyTarot/deck_detail.html',
                              context_instance=RequestContext(request, context))

def random_card(request):
    """ This is a view which simply chooses a card at random and gives you the 
        detail view for it. """
    
    # Get a list of all ids, choose one randomly, and get a handle to that Card object.
    card_ids = Card.objects.values('id')
    random_id = choice( card_ids )['id']
    card = Card.objects.get(pk=random_id)
    
    # Display the card detail view for the random card. Don't redirect, because this way you
    # can refresh the page and get another random card.
    return card_detail(request, card.tarot_index, card.deck.id)

def card_detail(request, tarot_index, deck_id):
    """ This is a view to show all information about a specific card in a 
        specific deck. """ 
    
    # If the card isn't in this deck, load the list of all cards in the deck
    try:
        card = Card.objects.get(tarot_index=tarot_index, deck=deck_id)
    except Deck.DoesNotExist:
        return tarot_card_detail(request, tarot_index)
    except Card.DoesNotExist:
        return deck_detail(request, deck_id)
    
    try:
        meaning = Meaning.objects.get(meaning_set=card.deck.meaning_set, tarot_index=tarot_index)
    except Meaning.DoesNotExist:
        meaning = Meaning()
    
    # For next and previous page links
    indices = get_nearest_indices(tarot_index, deck_id)
    
    # For the side navigation
    majors_list = MajorArcana.objects.filter(deck=deck_id).order_by('tarot_index')
    first_major = ''
    if majors_list.count() > 0:
        first_major = majors_list[0].tarot_index
    
    minors_list = MinorArcana.objects.filter(deck=deck_id).order_by('suit', 'tarot_index')
    first_minor = ''
    if minors_list.count() > 0:
        first_minor = minors_list[0].tarot_index
    
    # Gives us the list of suits which have no cards in them, for completion.
    empty_suit_list = []
    suits = Suit.objects.filter(deck=deck_id)
    for suit in suits:
        cards = MinorArcana.objects.filter(suit=suit.id)
        if cards.count() == 0:
            empty_suit_list += [suit]
            
    related_cards = Card.objects.filter(tarot_index=tarot_index).values('deck', 'deck__name')

    context = {'card': card,
               'meaning': meaning,
               'majors_list': majors_list,
               'minors_list': minors_list,
               'empty_suit_list': empty_suit_list,
               'related_cards': related_cards,
               'first_major': first_major,
               'first_minor': first_minor,
               'next_card_index': indices['next_index'],
               'previous_card_index': indices['previous_index'], }
    
    return render_to_response('diyTarot/card_detail.html',
                              context_instance=RequestContext(request, context))                              

def tarot_card_detail(request, tarot_index):
    """ This is a view to show all of the tarot cards of a particular index, 
        across all decks in the system. So, if you send it 1 (The Magician), it
        will display all Magician cards. """
     
    # Retrieve the card with the matching tarot_index from the right deck
    cards = Card.objects.filter(tarot_index=tarot_index).order_by('deck')
    meanings = Meaning.objects.filter(tarot_index=tarot_index)
    if meanings.count() > 0:
        meaning = meanings[0]
    else:
        meaning = {'keywords': 'None provided.',
                   'reversed_keywords': 'None provided.'}
    
    if len(cards) == 0:
        # If there is no matching tarot_index in any of the decks, then load
        # the view with all the cards
        return card_list(request)
    
    else:
        active_options = request.GET.copy()
        
        # Paginate the queryset and fetch the current page from the URL, with validation
        pages = Paginator(cards, 10, 3)
        current_page = get_current_page(active_options, pages)
        
        # The base url, since there is a different one for deck view and all cards view
        base_url = "/diytarot/cards/%s/" % tarot_index
        
        # For the next and previous links
        indices = get_nearest_indices(tarot_index)
        
        # For the side navigation
        default_deck_id = 1
        majors_list = MajorArcana.objects.filter(deck=default_deck_id).order_by('tarot_index')
        first_major = ''
        if majors_list.count() > 0:
            first_major = majors_list[0].tarot_index
        
        minors_list = MinorArcana.objects.filter(deck=default_deck_id).order_by('suit', 'tarot_index')
        first_minor = ''
        if minors_list.count() > 0:
            first_minor = minors_list[0].tarot_index
        
        # Gives us the list of suits which have no cards in them, for completion.
        empty_suit_list = []
        suits = Suit.objects.filter(deck=default_deck_id)
        for suit in suits:
            cards = MinorArcana.objects.filter(suit=suit.id)
            if cards.count() == 0:
                empty_suit_list += [suit]
                
        related_cards = Card.objects.filter(tarot_index=tarot_index).values('deck', 'deck__name')
        
        context = {'result_list': current_page,
                   'active_options': active_options,
                   'base_url': base_url,
                   'meaning': meaning,
                   'previous_card_index': indices['previous_index'],
                   'next_card_index': indices['next_index'],
                   'majors_list': majors_list,
                   'minors_list': minors_list,
                   'empty_suit_list': empty_suit_list,
                   'related_cards': related_cards,
                   'first_major': first_major,
                   'first_minor': first_minor}
        
        return render_to_response('diyTarot/tarot_card_detail.html',
                                  context_instance=RequestContext(request, context))

def reading(request, spread_id, deck_id):
    """ This is a view for displaying card readings on a given spread and deck. 
        By default the cards drawn are random, but if a string of saved cards called
        'cards' is passed in via query string it will try to load those cards, returning
        an error if the string is invalid."""
    
    try:
        spread = Spread.objects.get(pk=spread_id)
    except Spread.DoesNotExist:
        return spread_list(request)
    
    try:
        deck = Deck.objects.get(pk=deck_id)
        deck_name = deck.name
    except Deck.DoesNotExist:
        return deck_list(request)
 
    # Get all the positions in the spread and pull out the maximums for layout
    positions = CardPosition.objects.filter(spread=spread.id).order_by('index')
    num_positions = positions.count()
    max_x_coordinate = positions.aggregate(Max('x_coordinate'))['x_coordinate__max'] 
    max_y_coordinate = positions.aggregate(Max('y_coordinate'))['y_coordinate__max']  
    
    # Get all of the layout information for the template to use later
    layout = calculate_layout(positions, max_x_coordinate, max_y_coordinate)
    
    # If we have a query string, try to display the saved reading 
    if request.method == 'GET' and request.GET.get('cards') is not None:
        
        # Get the query string
        reading_string = request.GET.get('cards')
        try:
            # Try to parse out the saved reading encoding, and catch the exceptions.
            reading = load_saved_reading(reading_string, num_positions, deck.id)
        
        except (IndexError, TypeError, ValueError, Card.DoesNotExist):
            # Exceptions with custom messages are raised in the helper function,
            # then they are caught and their text is passed to the template for display
            return render_to_response('diyTarot/reading.html',
                                      {'error': 'Problem loading saved reading.',
                                       'spread': spread,
                                       'deck': deck })
    else : 
        # Otherwise, create a random reading that is different every time the page is loaded.
        # Select all cards, filter by the chosen deck, put in random order and then 
        # slice off the number of cards that appear in the spread
        random_cards = Card.objects.all().filter(deck=deck_id).order_by('?')[:num_positions]
        reversal_odds = [False, False, False, False, False, False, False, True, True, True]
        
        reading = []
        for card in random_cards:
            reading += [{'card': card,
                     'reversed': choice(reversal_odds)}]
            
    # Put together the card object, position object, layout coordinates for display in the template
    # and generate a save string for the thrown cards.
    card_list = []
    saved_card_list = []
    for (thrown_card, position, coordinates) in zip(reading, positions, layout['coordinates']):
        
        card_list += [(position, thrown_card, coordinates)]
        saved_card_list  += ["%d.%d" % (thrown_card['card'].tarot_index, 
                                        int(thrown_card['reversed']))]
    
    # Build the string to re-create this reading.  
    save_string = (',').join(saved_card_list)
    
    # Lists for use in the navigation menu
    deck_list = Deck.objects.values('id', 'name').order_by('name')
    spread_list = Spread.objects.values('id', 'title').order_by('title')
    
    deck_options = {}
    # Check if there is a default deck stored in the current session
    if 'deck' in request.session:
        deck_options['session_deck_id'] = request.session['deck']
    else:
        deck_options['session_deck_id'] = '1'
        
    deck_options['session_deck_name'] = Deck.objects.get(id=deck_options['session_deck_id']).name
    deck_options['display_deck_id'] = deck_id
    deck_options['display_deck_name'] = deck_name
    
    context = {'spread': spread,
               'card_list': card_list,
               'save_string': save_string,
               'layout': layout['sizes'],
               'deck_options': deck_options,
               'deck_list': deck_list,
               'spread_list': spread_list,} 
        
    return render_to_response('diyTarot/reading.html',
                              context_instance=RequestContext(request, context))
    
def update_reading_settings(request, spread_id):
    """ This is the view that sets the persistent settings for readings: which deck to use
        and whether to enable card reversals. It is invoked when the user updates their reading
        settings. """
    
    # Get the form data, see if it's valid, and if needed update
    # the session variables.
    try:
        deck_id = int(request.GET.get('deck', 1))
    except ValueError:
        deck_id = 1
        
    # Check if the deck is a valid deck in the system
    deck = Deck.objects.filter(id=deck_id)
    if deck.count() > 0:
        request.session['deck'] = deck_id

    # Then just invoke the reading view
    target = "/diytarot/reading/%s/%s/" % (spread_id, deck_id)
    return redirect(target)

def random_reading(request):
    """ This is a view to get you directly to a tarot reading without browsing through
        the various spreads. Then, you can change the reading settings via the sidebar. """
        
    deck_id_list = Deck.objects.values_list('id')
    deck_id = int(choice(deck_id_list)[0])
    
    spread_id_list = Spread.objects.values_list('id')
    spread_id = int(choice(spread_id_list)[0])
    
    # Then just invoke the reading view
    target = "/diytarot/reading/%s/%s/" % (spread_id, deck_id)
    return redirect(target)

def two_cards_exercise(request):
    """ This is a view for the game/exercise Two Cards, a Question, and a Sentence, which
        chooses two random cards and a random question and asks the user to make a 
        one-sentence interpretation. """
    
    
        
    context = {'deck_options': None,
               'deck_list': deck_list,
               'card_list': card_list,} 
        
    return render_to_response('diyTarot/reading.html',
                              context_instance=RequestContext(request, context))
    


  