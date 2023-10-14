from django.contrib import admin

from posts.models import Company, Post, Category, Product, Region, SubCategory, PostBody, Theme, Sector

admin.site.register(PostBody)


class PostBodyInline(admin.TabularInline):
    model = PostBody
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [PostBodyInline]

    list_display = ('author', 'title', 'status', 'views', 'published_at', 'created_at', 'updated_at')
    list_filter = ('published_at', 'status')
    search_fields = ('title',)
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'
    exclude = ['slug', 'views', 'author', 'body', 'excerpt']

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)
