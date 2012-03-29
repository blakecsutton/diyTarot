from django.template import Library

register = Library()

def remove_and_reencode(query_dict, keys):
    """ Filter that accepts a QueryDict and a comma-separated string of keys. For every key in the list
        which actually appears in the provided QueryDict, this filter removes that key
        and returns the results of re-encoding the url based on the changed query_dict, without the keys.
        The original query_dict is not modified. 
        
        Usage: q|remove_and_urlencode:'deck,page'
    """
    
    # Turn the comma-separated string into a list of keys
    key_list = keys.rsplit(',')
    temp = query_dict.copy()    
    
    for key in key_list:
        if key in query_dict:
            del temp[key]
            
    return temp.urlencode()

register.filter(remove_and_reencode)