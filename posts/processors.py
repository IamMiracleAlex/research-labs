from posts.models import SubCategory


def get_categories(request):
    sub_categories = SubCategory.objects.all()
    return {
        'subcategories': sub_categories}
