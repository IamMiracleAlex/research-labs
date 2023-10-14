import random


def get_random_obj(queryset:list, number: int=None):
    if not queryset:
        return None
    queryset_list = list(queryset)
    if number and queryset.count() <= number:
        return queryset
    return (
        random.sample(queryset_list, number)
        if number
        else random.choice(queryset_list)
    )


def get_single_random_obj(queryset):
    if not queryset:
        return None
    if len(queryset) < 2:
        return queryset.first()
    return random.choice(queryset)


def format__date(date):
    """Format date string to django date format"""
    return date.strftime("%Y-%m-%d")
