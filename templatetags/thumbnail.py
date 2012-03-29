import os
import Image
from django.template import Library

register = Library()

# Custom filter to do thumbnail automatically -- from django-snippets.com
# Example usage inside a template:
# <img src="{{ object.image.url }}" alt="original image"> 
# <img src="{{ object.image|thumbnail }}" alt="image resized to default 104x104 format"> 
# <img src="{{ object.image|thumbnail:'200x300' }}" alt="image resized to 200x300">
def thumbnail(image_file, size='104x104', reverse=False):
    
    # Parse out the input string into x and y dimension integers
    x, y = [int(x) for x in size.split('x')]
    
    # Separate the file path into the directory location and the filename
    # Split the filename into the actual name and the extension (including the .)
    file_path = image_file.path
    file_head, file_name = os.path.split(file_path)
    base_name, file_format = os.path.splitext(file_name)
    
    # Create the full path to the new thumbnail. Put it in a subdirectory of the location
    # of the input image's path, named "thumbs", and append the size of the thumb to the original name.
    # So an input of ("C:/haters/your_mom.jpg", "100x100") would produce "C:/haters/thumbs/your_mom_100x100.jpg"
    if reverse:
        thumb_name = base_name + '_' + size + '_reversed' + file_format
    else:
        thumb_name = base_name + '_' + size + file_format
        
    thumb_head = os.path.join(file_head, 'thumbs')
    thumb_path = os.path.join(thumb_head, thumb_name)
    
    # If the file already exists and the last modified time of the original file is more recent than 
    # the last modified version of the thumbnail, delete the thumb.
    if os.path.exists(thumb_path) and os.path.getmtime(file_path)>os.path.getmtime(thumb_path):
        os.unlink(thumb_path)
        
    # If the thumbnail doesn't already exist (or has been deleted above), create it.
    if not os.path.exists(thumb_path):
        
        # Check for existence of the thumbs subdirectory, and if it's not there, create it.
        if not os.path.exists(thumb_head):
            os.mkdir(thumb_head)
        
        image = Image.open(file_path)
        image.thumbnail([x, y], Image.ANTIALIAS)
        
        # Handle the normal, upright, unreversed case
        if not reverse:
            
            try:
                image.save(thumb_path, image.format, quality=90, optimize=1)
            except:
                image.save(thumb_path, image.format, quality=90)
        
        else:
            # Otherwise if reversed is true making a reversed thumbnail (flipped in the y direction)
            # Rotate, unlike thumbnail, does not modify the image in place, so we need to rename.
            reversed_image = image.rotate(180)
            
            try:
                reversed_image.save(thumb_path, image.format, quality=90, optimize=1)
            except:
                reversed_image.save(thumb_path, image.format, quality=90)
            
    # Now get the URL of the image file (as opposed to its directory location), discarding
    # the image filename part since it is the same for both url and file path,
    # then use it to create the URL for the request thumbnail.
    url_head = os.path.split(image_file.url)[0]
    thumb_url = os.path.join(url_head, 'thumbs', thumb_name)
            
    # Finally, return the url of the thumbnail so it can be used in the template
    return thumb_url

# Custom filter to do vertical flip automatically -- This is just syntactic sugar and calls
# thumbnail with a different option. Usage is the same, except use reversed_thumbnail instead.
def reversed_thumbnail(image_file, size='104x104'):
    
    return thumbnail(image_file, size, reverse=True)

register.filter(thumbnail)
register.filter(reversed_thumbnail)
