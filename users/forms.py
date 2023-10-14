from django import forms
from django.utils.translation import ugettext_lazy as _

from users.models import User


class LoginForm(forms.Form):
    email = forms.CharField(label='Email', required=True)
    password = forms.CharField(
        label='Password',
        required=True,
        widget=forms.PasswordInput()
    )

    fields = ['email', 'password']


class RegistrationForm(forms.Form):
    DATE_FORMATS = ['%Y/%m/%d']

    first_name = forms.CharField(
        max_length=50,
        label=''

    )
    last_name = forms.CharField(
        max_length=50,
        label=''
    )
    email = forms.EmailField(
        max_length=60,
        label=''
    )
    company_name = forms.CharField(
        max_length=50,
        label=''
    )
    job_title = forms.CharField(
        max_length=50,
        label=''
    )
    country_or_region = forms.CharField(
        max_length=50,
        label=''
    )
    password = forms.CharField(
        max_length=30,
        label='',
        widget=forms.PasswordInput,
    )
    confirm_password = forms.CharField(
        max_length=30,
        label='',
        widget=forms.PasswordInput
    )

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', None)
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs = {
            'placeholder': _(u'First name'),
            'class': 'form-control'
        }
        self.fields['last_name'].widget.attrs = {
            'placeholder': _(u'Last name'),
            'class': 'form-control'
        }
        self.fields['email'].widget.attrs = {
            'placeholder': _(u'Email'),
            'class': 'sizefull form-control'
        }
        self.fields['company_name'].widget.attrs = {
            'placeholder': _(u'Company Name'),
            'class': 'form-control'
        }
        self.fields['job_title'].widget.attrs = {
            'placeholder': _(u'Job Title'),
            'class': 'form-control'
        }
        self.fields['country_or_region'].widget.attrs = {
            'placeholder': _(u'Country/Region'),
            'class': 'form-control'
        }
        self.fields['password'].widget.attrs = {
            'placeholder': _(u'Password'),
            'class': 'form-control'
        }
        self.fields['confirm_password'].widget.attrs = {
            'placeholder': _(u'Confirm Password'),
            'class': 'form-control'
        }

    error_messages = {
        'short_password': _(
            "The password is too short, minimum of 6 characters."
        ),
        'user_exists': _(
            "This email address is already registered, "
            "use the forgot password link to recover it."
        ),
        'password_mismatch': _(
            "The password and password "
            "confirmation do not match."
        ),
    }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email):
            raise forms.ValidationError(
                self.error_messages['user_exists'],
                code='user exists'
            )
        return email

    def clean(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password and len(password) < 6:
            raise forms.ValidationError(
                self.error_messages['short_password'],
                code='short_password',
            )
        if password != confirm_password:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password mismatch'
            )

        return self.cleaned_data

    def save(self, commit=True):
        try:
            user = User.objects.create_user(
                last_name=self.cleaned_data.get('last_name'),
                first_name=self.cleaned_data.get('first_name'),
                email=self.cleaned_data.get('email'),
                password=self.cleaned_data.get('password'),
            )
            return user
        except Exception as e:
            raise ValueError(
                f"{str(e)}"
            )
