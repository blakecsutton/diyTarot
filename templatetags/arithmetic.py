from django.template import Library

register = Library()

def float_add(value, arg):
    "Add the arg and the value, taking into account floats"
    return float(value) + float(arg)

def multiply(value, arg):
    "Multiplies the arg and the value"
    return int( float(value) * float(arg) )

def subtract(value, arg):
    "Subtracts the arg from the value"
    return int(value) - int(arg)

def divide(value, arg):
    "Divides the value by the arg"
    return int( float(value) / float (arg) )

register.filter(multiply)
register.filter(subtract)
register.filter(divide)
register.filter(float_add)