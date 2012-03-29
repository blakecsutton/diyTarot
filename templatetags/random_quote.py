from django.template import Library
from random_line import random_line

register = Library()

def random_quote(filename):
    """ Filter that reads a file and returns one line at random, split
        into two pieces (quote and author) as a list.
        
        Usage: 'diytarot/files/sayings.txt'|random_quote
    """
    
    quote = random_line(filename)
    
    divided = quote.split('~')
    if len(divided) > 0:
        return divided
    else:
        return ["OH MY GOD WHO'S FLYING THIS THING!?!!", "..oh right, that would be me."]

register.filter(random_quote)