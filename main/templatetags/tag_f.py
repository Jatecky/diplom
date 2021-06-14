from django import template   
  
register = template.Library()  
  
@register.simple_tag  
def carry_str(str, count_symbol):
    _list = str.split()
    list_str = ['']
    index = 0
    for word in _list:
        if len(list_str[index]) + 1 + len(word)< count_symbol or len(word)> count_symbol:
            list_str[index] += ' ' +  word
        else:
            list_str.append(word)
            index += 1
    return list_str

@register.simple_tag
def my_if(value1, value2):
    if value1==value2:
        return True
    else:
        return False