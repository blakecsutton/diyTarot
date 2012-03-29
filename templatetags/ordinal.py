from django.template import Library

register = Library()

def ordinal(text):
    """ Filter that returns the suffix of its input's ordinal (1st, 2nd, 3rd, 4th, etc).
        If the input is not a non-negative integer, this filter returns nothing 
        (as no ordinal suffix is appropriate).
        
        Usage: q|ordinal
        Examples: 1|ordinal -> 1st, 
                 16|ordinal -> 16th
                 211|ordinal -> 211th
                 201|ordinal -> 201st
                 dogs|ordinal -> dogs
                 100.0|ordinal -> 100.0
    """
    try: 
        number = int(text)
    except ValueError:
        return text
    
    # Pull out ones digit and tens digit for analysis
    ones = number % 10
    tens = number % 100
    if number >= 0:
        if tens == 1:
            suffix = 'st'
        else:
            if ones == 1:
                suffix = 'st'
            elif ones == 2:
                suffix = 'nd'
            elif ones == 3:
                suffix = 'rd'
            else:
                suffix = 'th'
    else:
        # Leave negative numbers alone
        suffix = ''
    
    return str(number) + suffix


register.filter(ordinal)