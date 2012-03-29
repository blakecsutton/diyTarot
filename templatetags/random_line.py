from django.conf import settings
from django.template import Library
import os
import random

register = Library()

def random_line(filename):
    """ Filter that reads a file and returns one line at random.
        
        Note that the file HAS to be somewhere inside MEDIA_ROOT.
    """
    try:
      os.chdir(settings.MEDIA_ROOT)
      
      file_size = os.stat(filename)[6]
      
      target_file = open(filename, 'r')
    
      #Seek to a place in the file which is a random distance away
      #Mod by file size so that it wraps around to the beginning
      target_file.seek(random.randint(0,file_size-1))
  
      #dont use the first readline since it may fall in the middle of a line
      target_file.readline()
      
      #this will return the next (complete) line from the file
      line = target_file.readline().strip()
      
      target_file.close()
    
      # If the previous line happened to be the last one, getting the next line
      # will give us a blank line, so in that case just give the first line of the file
      if line is None or len(line) <= 0:
          
          target_file = open(filename, 'r')
          line = target_file.readline().strip()
          target_file.close()
          
    except (OSError, IOError):
      line = ""

    return line

register.filter(random_line)