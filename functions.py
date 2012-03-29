from models import Card
from django.db.models import Max
from django.db.models import Min
from django.db.models import Q
from django.core.paginator import InvalidPage, EmptyPage

def get_nearest_indices(tarot_index, deck_id=None):
    """ This is a helper function for finding the indices of the next and previous cards in a deck,
        by tarot_index. It handles gaps in the set by querying the database, and
        also automatically loops around when you reach the beginning or end of
        the sequence of cards. """
    
    before_filter_args = {'tarot_index__lt': tarot_index}
    after_filter_args = {'tarot_index__gt': tarot_index}
    if deck_id is not None:
        before_filter_args['deck'] = deck_id
        after_filter_args['deck'] = deck_id
    
    # Find the minimum index less than the current tarot_index
    min_index = Card.objects.filter(**before_filter_args).aggregate(
                                                Min('tarot_index'))['tarot_index__min'] 
                                                
    # Find the maxmimum index less than the curent tarot_index                                            
    previous_index = Card.objects.filter(**before_filter_args).aggregate(
                                                Max('tarot_index'))['tarot_index__max']
    
    # Find the minimum index greater than the current tarot_index                                                                           
    next_index = Card.objects.filter(**after_filter_args).aggregate(
                                                Min('tarot_index'))['tarot_index__min']     
    
    # Find the maximum index greater than the current tarot_index                                                                   
    max_index = Card.objects.filter(**after_filter_args).aggregate(
                                                Max('tarot_index'))['tarot_index__max'] 
    
    if max_index is None:
        max_index = tarot_index
    
    if min_index is None:
        min_index = tarot_index
        
    if previous_index is None:
        previous_index = max_index
        
    if next_index is None:
        next_index = min_index
        
    return {'next_index': next_index,
            'previous_index': previous_index}
    
def calculate_layout(positions, max_x_coordinate, max_y_coordinate):
    """ Helper function for the reading view that converts from the logical coordinates for positions
        used in the database to the screen coordinates used for layout in the template.
        Also calcultes the scaled size of the cards and the total size of the container
        needed to hold all the cards in the spread.  """
    
    # TODO: make this dynamic based on the size of the spread, within some min and max.
    
    # This depends on the images used. This should be made into an application setting
    # or found dynamically at some point.
    aspect_ratio = 0.6
       
    # Adjustable aspects of the layout, currently hardcoded. 
    card_height = 150
    card_x_padding = 20
    card_y_padding = 30
    
    # The width as derived from the height and aspect_ratio
    card_width = int(card_height * aspect_ratio)
    thumbnail_string = "%dx%d" % (card_width, card_height)

    # Calculate the total height and width containing the thrown cards
    height = ((max_y_coordinate + 1) * (card_height + card_y_padding))
    width = ((max_x_coordinate + 1) * (card_width + card_x_padding))
    
    # Calculate the coordinates, in pixels, for each card 
    coordinate_list = []
    for position in positions:
        
        top = position.y_coordinate * (card_height + card_y_padding)
        left = position.x_coordinate * (card_width + card_x_padding)
        coordinate_list += [{'top': top,
                             'left': left}]
        
    # Return everything in a dictionary
    return {'sizes' :{'height': height,
                      'width': width,
                      'card_width': card_width,
                      'card_height': card_height,
                      'thumbnail_string': thumbnail_string},
                      'coordinates': coordinate_list}

def load_saved_reading(reading_string, num_positions, deck_id):
    """ Helper function for the reading view which attempts to parse out a string encoding 
        of a particular set of cards, including reversals. If the encoding is invalid 
        (due to not matching a valid card, having the wrong format, etc) then an
        exception is thrown with a custom error message. Otherwise it returns a list of
        thrown card dictionaries with Card objects and reversal status."""
    
    # Format: card0_id.reversed,card1_id.reversed ...
    saved_card_list = reading_string.split(',')
    
    # Check the number of items in the string against the number positions
    if len( saved_card_list ) != num_positions:
        raise IndexError('Number of cards in the save string does not match the number of' +
                                ' positions in the spread.')
     
    # Parse each card, raising an exception if there is a problem at any point
    cards = []
    for saved_card in saved_card_list:
        
        # Separate the card id and the reversal status
        thrown_card = saved_card.split('.')
        if len(thrown_card) != 2:
            raise IndexError('Save string is incorrectly formatted or missing information.')
        
        # Convert from string to int and boolean, respectively. 
        try:
            tarot_index = int(thrown_card[0])
        except ValueError:
            raise ValueError('The save string must contain a series of two integers separated by a ' +
                             'period, with commas as separators.')
            
        if thrown_card[1] == '0':
            reversed = False
        elif thrown_card[1] == '1':
            reversed = True
        else:
            raise ValueError('Reversal encoding for a card must be 0 or 1.')
        
        # Look up the card by id. Note this is the primary key, not the tarot_index.
        try:
            card = Card.objects.get(tarot_index=tarot_index, deck=deck_id,)
        except Card.DoesNotExist:
            raise Card.DoesNotExist('The save string includes a card that does not exist.')
        
        # Save the card and reversal info into a dictionary together    
        cards += [{'card': card, 
                   'reversed': reversed} ]
         
    return cards;


def validate_integer(input_dict, key):
    """ If the key is present in input_dict and is not an integer, remove it. Return
        True if the key is in the dictionary and an integer, and false otherwise. """
    
    if key in input_dict:
        try: 
            input_dict[key] = int(input_dict[key])
            return True
        
        except ValueError:
            del input_dict[key]
        
    return False    

def validate_string(input_dict, key, allowed_values):
    """ If the key is present in input_dict but is not equal to one of the items in the
        allowed_values list, then remove it. Return True if the key is in the dictionary
        and one of the allowed_values, otherwise False. """

    if (key in input_dict and 
        input_dict[key] in allowed_values):
        return True
    else:
        return False   

def apply_key_filter(active_options, filter_args, option_name, key_name):
    """ This is a helper function for display options that relate to model keys, e.g.
        displaying cards from a specific deck. It accepts a QueryDict of display options
        (probably from the GET or POST header), a dictionary of keyword arguments
        used for modifying the QuerySet, the name of the option (used to index into display_options),
        and the corresponding key name used in the QuerySet.
        
        Example: apply_key_filter(active_options, filter_args, 'deck', 'deck')
    """
    if validate_integer(active_options, option_name):
        filter_args[key_name] = active_options[option_name]


def apply_string_option_filter(active_options, keyword_args, option_name, option_values):
    """ This is a helper function for options which use pre-definied set of allowed string
    inputs (e.g., radio buttons, not a search box), which correspond individual ways to affect
    the QuerySet.

        Inputs:
        display_options: a QueryDict of input parameters used to look up options
        keyword_args: keyword argument dictionary used to affect the QuerySet (via filter, order_by, etc.)
        option_name: used to index into display_options. Example: "cards"
        options_values: dictionary of dictionaries for describing allowed option
                        values and which filtering arguments go with each one.
                        Example: {"majors": {'tarot_index__lt': 22},
                                  "minors": {'tarot_index__gt': 21}}
   """                     

    # Validate the string, removing from dispaly_options if input was invalid
    if validate_string(active_options, option_name, option_values):
        
        # Index into the display_options dictionary to get the dictionary matching
        # the current choice.
        selected_value = active_options[option_name]
        
        # Iterate over the keyword arguments that define how this particular choice
        # affects the QuerySet, updating the filter_args dictionary to match.
        for keyword, keyword_value in option_values[selected_value].iteritems():
            keyword_args[keyword] = keyword_value
            
def apply_card_filter(active_options, filter_args):
    """ This is a helper function for filtering cards based on whether
        they are in the major or minor arcana. All it really does it set up the
        arguments to send to the string options function. """
        
    option_name = 'cards'       
    option_values = {'majors': {'tarot_index__lt': 22},
                     'minors': {'tarot_index__gt': 21} }
    
    apply_string_option_filter(active_options, filter_args, option_name, option_values)
    

def apply_suit_filter(active_options, filter_args):    
    """ This is a helper function for filtering cards based on their suit. It really just
    sets up inputs and passes the work on the key filtering function. However, it does
    check if the display_options are set to display the minor arcana,, because it doesn't
    make sense to filter on suit unless showing the minor arcana."""
    
    if ('cards' in active_options and
        active_options['cards'] == 'minors'):
        
        apply_key_filter(active_options, filter_args, 'suit', 'suit__suit')

def apply_rank_filter(active_options, filter_args):
    """ This is a helper function for filtering cards based on their rank. It really just
    sets up inputs and passes the work on the string options function. If the cards option
    is not set to 'minors' then we set that option, because it doesn't make sense to 
    filter by rank if not displaying the minor arcana."""
    
    if ('cards' in active_options and
        active_options['cards'] == 'minors'):

        option_name = 'ranks'
        option_values = {'acefive': {'rank__lte': 5},
                         'fiveten': {'rank__lte': 10, 
                                     'rank__gte': 5},
                         'court': {'rank__gt': 10}}
        
        apply_string_option_filter(active_options, filter_args, option_name, option_values)
    
        
def apply_sorting_order(active_options, order_args):
    """ This is a helper function for sorting the cards in a query. Since sorting order is less
        complex than filtering, order_args is a list of fields to sort on."""
    
    option_name = 'order_by'
    option_values = {'rank': ['rank', 'suit__suit'],
                     'suit': ['tarot_index', 'deck']}
    
    # Default sorting order is by tarot_index
    if not validate_string(active_options, option_name, option_values):
        active_options[option_name] = 'suit'
        
    selected_option = active_options[option_name]
    order_args += option_values[selected_option]

def apply_keyword_search_filter(active_options, query_list):
  option_name = 'search'
  
  if option_name in active_options:
    search_term = active_options[option_name]
    
    # Any value is valid except nothing
    if len(search_term) > 0:
        # OR together Q objects for all the fields to search, since a match on any of them is ok.
        search_query = [Q(keywords__icontains=search_term)]
        
        query_list += search_query
    
def apply_card_search_filter(active_options, query_list):
  """ This is a helper function for searching cards. It only checks the title, caption, and
      description fields, and it uses Q's in order to giving OR'ing behavior. """
      
  option_name = 'search'
  if option_name in active_options:
    search_term = active_options[option_name]
    
    # Any value is valid except nothing
    if len(search_term) > 0:
        # OR together Q objects for all the fields to search, since a match on any of them is ok.
        search_query = [Q(title__icontains=search_term) |
                        Q(caption__icontains=search_term) |
                        Q(description__icontains=search_term)]
        
        query_list += search_query
        

def apply_spread_search_filter(active_options, query_list):
    """ This is a helper function for searching Spreads. Since it is a search
        action, it operates around Q's which are OR'd together, rather than
        using keyword arguments. It takes a QueryDict of all the currently
        active options, and a list of Q objects which it will add to if
        the search option is activated. """
    
    option_name = 'search'
    if option_name in active_options:
        search_term = active_options[option_name]
        
        # Since this is a search filter, any value is valid except for a blank.
        if len(search_term) > 0:
            
            # OR together the Q objects for each field we want to search
            search_query = [Q(title__icontains=search_term) |
                            Q(description__icontains=search_term)]
            
            # Append this query to the list so that the overal query will be AND'd together.
            query_list += search_query
            
def apply_spread_size_filter(active_options, query_list):
    """ This is a helper function for filtering spreads by the number of
        cards. It uses Q objects instead of using the keyword arguments directly because
        It's used with spread list, for searching. """
    
    option_name = 'size'
    option_values = {'small': {'size__lte': 3},
                     'medium': {'size__lte': 7,
                                'size__gte': 4},
                     'large': {'size__gte': 8}}      
    
    if validate_string(active_options, option_name, option_values):
 
        selected_value = active_options[option_name]
        
        # Stick the dictionary of filter argument into the Q objects as keyword arguments
        query_list += [Q(**option_values[selected_value])]

def get_current_page(active_options, pages):
    """ This is a function to separate the logic for fetching the current page from
        the current display options, checking if it is valid based on the underlying
        QuerySet, and returning a default page if it is not. Accepts an active_options
        dictionary of all currently active display options and a Paginator. """
        
    # If the page number wasn't specified or is not an integer, set it to 1
    try:
        page_number = int(active_options.get('page', 1))
    except ValueError:
        page_number = 1
    
    # Check if page is in range, if not deliver last page
    try:
        current_page = pages.page(page_number)
    except (EmptyPage, InvalidPage):
        page_number = pages.num_pages
        current_page = pages.page( page_number )  
    
    # Update the active options value for the page, in case it was originaly not present
    # or out of range.  
    active_options['page'] = page_number  
        
    return current_page
    
        
