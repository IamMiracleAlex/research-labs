from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse

from taggit.managers import TaggableManager
from cloudinary.models import CloudinaryField


class CustomPostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
    def deleted(self):
        return super().get_queryset().filter(is_active=False)


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        super().save(*args, **kwargs)


class SubCategory(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Sub categories"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        super().save(*args, **kwargs)


class BaseSectorTheme(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)  
    class Meta:
        abstract = True


class Sector(BaseSectorTheme):
    pass

class Theme(BaseSectorTheme):
    pass

class Product(BaseSectorTheme):
    pass

class Region(BaseSectorTheme):
    pass

class Company(BaseSectorTheme):
    class Meta:
        verbose_name_plural = 'Companies'


class Post(models.Model):
    DRAFT, PUBLISHED = 'Draft', 'Published'
    STATUS_CHOICES = (
        (DRAFT, DRAFT),
        (PUBLISHED, PUBLISHED),
    )

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, blank=True, null=True)
    author = models.ForeignKey(
        'users.User',
        null=True,
        on_delete=models.SET_NULL
    )
    body = models.TextField(blank=True, null=True)
    excerpt = models.TextField(blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=DRAFT
    )
    image = CloudinaryField('image')
    views = models.BigIntegerField(default=0)
    subcategories = models.ManyToManyField('posts.SubCategory', blank=True)
    is_premium = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)
    themes = models.ManyToManyField(
        'posts.Theme',
        blank=True,
        related_name='posts'
    )
    sectors = models.ManyToManyField(
        'posts.Sector',
        blank=True,
        related_name='posts'
    )
    products = models.ManyToManyField(
        'posts.Product',
        blank=True,
        related_name='posts'
    )
    regions = models.ManyToManyField(
        'posts.Region',
        blank=True,
        related_name='posts'
    )
    companies = models.ManyToManyField(
        'posts.Company',
        blank=True,
        related_name='posts'
    )
    is_active = models.BooleanField(default=True)

    objects = CustomPostManager()


    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    @property
    def formatted_categories(self):
        return ', '.join([theme.name for theme in self.themes.all()] + [sector.name for sector in self.sectors.all()])

    def publish(self):
        self.published_at = timezone.now()
        self.status = self.PUBLISHED
        self.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    @property
    def short_body(self):
        if self.sections.exists():
            return self.sections.first().text

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"slug": self.slug})


class PostBody(models.Model):
    '''Post Section, used in giving several sections to post body'''

    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name="sections"
    )
    text = models.TextField(blank=True, null=True)
    title = models.CharField(
        verbose_name='Section Title',
        max_length=250,
        null=True,
        blank=True
    )
    slug = models.SlugField(max_length=250, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.title}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ReadPost(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    total_posts = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.post}"
