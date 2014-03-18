__author__ = 'Tarzan'
import re

def camel_case_to_underscore(str):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def underscore_to_camel_case(str):
    pass

def camel_case_to_title(str):
    pass

def underscore_to_title(str):
    pass