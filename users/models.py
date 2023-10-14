from django.db import models
from django.contrib.auth.models import AbstractUser

from users.managers import CustomUserManager


class User(AbstractUser):
    '''
    The model to store users

    - username: is None (we don't authenticate with username)
    - email: the user email, unique
    '''
    username = None
    email = models.EmailField(unique=True)
    company_name = models.CharField(null=True, blank=True, max_length=50)
    job_title = models.CharField(null=True, blank=True, max_length=50)
    country_or_region = models.CharField(null=True, blank=False, max_length=50)
    is_premium = models.BooleanField(default=False)

    photo = models.ImageField(upload_to='users/', null=True, blank=True)
 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __str__(self):
        return self.email


class PremiumRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=255, null=True)
    short_message = models.TextField(blank=True, null=True)
    assignee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="assignee"
    )
    redirected_from = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    def __str__(self) -> str:
        return f"{self.user} - {self.company}"
