from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth import logout, authenticate, login
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from users.forms import LoginForm, RegistrationForm
from django.core.signing import Signer
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode
)
from django.utils.encoding import force_bytes, force_text
from django.utils import timezone

from users.models import PremiumRequest, User
from users.tokens import account_activation_token
from users.forms import LoginForm
from posts.models import Post, ReadPost


class LoginView(View):
    template = 'login.html'

    def get(self, request):

        form = LoginForm()
        context = {
            'form': form,
        }
        return render(request, template_name=self.template, context=context)

    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return HttpResponse("Logged In", status=200)

            return HttpResponse("Invalid password or username", status=400)

        else:
            return HttpResponse(form.errors)


class LogoutView(View):

    def get(self, request):
        logout(request)
        return HttpResponse("Logged Out")


class RegistrationView(View):

    def get(self, request):
        form = RegistrationForm()
        context = {
            "form": form
        }
        return render(
            request,
            template_name="signup.html",
            context=context
        )

    def post(self, request):
        username = request.POST.get('email')
        password = request.POST.get('password')
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(request, username=username, password=password)
            # TODO: Complete the email verification part
            # verification thingy.
            # signer = Signer()
            # signed_value = signer.sign(profile.email)
            # profile.key = ''.join(signed_value.split(':')[1:])
            # profile.save()

            # Send the user an email to confirm registration
            # try:
            #     notify(request, user)
            #     return HttpResponseRedirect(reverse('index'))
            # except Exception as e:
            #     raise ValueError(f"{str(e)}")
            #     return HttpResponseRedirect(reverse('user:account'))
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('users:plan_activate'))
        return render(request, 'signup.html', {'form': form})


def notify(request, user):
    user = user
    current_site = request.get_host()
    domain = ''
    if current_site.startswith('localhost'):
        domain = 'http://' + current_site
    else:
        domain = "https://" + current_site

    context_dict = {
        'name': '{0} {1}'.format(user.last_name, user.first_name),
        'user': user,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token().make_token(user),
    }
    txt_message = render_to_string(
        'accounts/account_activation_email.txt',
        context_dict
    )
    html_message = render_to_string(
        'accounts/account_activation_email.html',
        context_dict
    )
    subject, from_email, to = (
        'WELCOME: Verification Required',
        'no-reply@herbalx.ng',
        user.username
    )
    msg = EmailMultiAlternatives(
        subject,
        txt_message,
        from_email,
        [to]
    )
    msg.attach_alternative(html_message, "text/html")
    try:
        msg.send()
        messages.info(
            request,
            "Please check your email to activate your account."
        )
        user.is_active = False
        user.save()
    except Exception as e:
        # TODO: Refactor this and ensure that the user either
        # gets an email or fails for him to retry

        # I activate the user if I can't send email and log.
        messages.info(
            request,
            (
                "Sorry! An error occurred while trying "
                "to create your account. Please try again"
                f"{str(e)}"
            )
        )


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if (
            user is not None
            and account_activation_token.check_token(user, token)
        ):
            user.is_active = True
            user.save()
            activation_success(request, user)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return HttpResponseRedirect(reverse('users:account'))
    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist
    ):
        user = None
    return HttpResponseRedirect(reverse('index'))


def activation_success(request, user):
    """
    Just sent a mail to the user to confirm activation
    """
    context_dict = {
        'name': '{0} {1}'.format(user.last_name, user.first_name),
        'user': user,
    }
    txt_message = render_to_string(
        "accounts/verify_success.txt",
        context_dict
    )
    html_message = render_to_string(
        "accounts/verify_success.html",
        context_dict
    )
    subject, from_email, to = (
        "CONGRATULATIONS! Account Activated",
        'no-reply@coresight.com',
        user.username
    )
    msg = EmailMultiAlternatives(subject, txt_message, from_email, [to])
    msg.attach_alternative(html_message, "text/html")
    try:
        msg.send()
        messages.info(
            request,
            "Account Successfully Activated"
        )
    except Exception as e:
        messages.info(
            request,
            (
                "Sorry! An error occurred while trying"
                " to create your account. Please try again"
                f" {str(e)}"
            )
        )


class AccountView(View):
    template = 'users/profile.html'

    def get_recommended_posts(self, posts):
        
        returning_user = False

        # get viewed posts and convert to a list
        previously_viewed_posts = self.request.COOKIES.get('viewed_posts', '')
        if previously_viewed_posts:
            returning_user = True
            previously_viewed_posts = [int(i) for i in previously_viewed_posts.split('-') if i]
            # get associated tags and filter  out posts with similar tags
            interests = [
                post.tags.all()
                for post in posts.filter(id__in=previously_viewed_posts)]
            interests = [tag.id for sublist in interests for tag in sublist]

            if interests:
                posts = posts.filter(tags__in=interests).distinct()

        return posts[:10] if returning_user else posts.none()

    @method_decorator(login_required())
    def get(self, request):
        posts = Post.objects.filter(status=Post.PUBLISHED)
        now = timezone.now()

        diff_since = 0
        read_posts = ReadPost.objects.filter(user=request.user).select_related('post')
        if read_posts:
            diff_since = abs(posts.count() - read_posts.first().total_posts)
        recent_posts = posts.order_by('-published_at')[:10]
        recommended_posts = self.get_recommended_posts(posts)
        context = {
            'read_posts': read_posts,
            'diff_since': diff_since,
            'recent_posts': recent_posts,
            'recommended_posts': recommended_posts,
            "total_read_posts": read_posts.filter(date__month=now.month).count(),
            "today": now.strftime("%B %d, %Y"),
            "month": now.strftime("%B"),
            "total_reccommended": recommended_posts.count()

        }
        return render(request, template_name=self.template, context=context)


class PlanActivateView(View):
    template_name = 'users/plan.html'

    def get(self, request):
        plan = request.GET.get("plan")
        if plan:
            if request.user.is_authenticated:
                return HttpResponseRedirect(reverse('users:account'))
        return render(request, template_name=self.template_name, context={})


class PremiumRequestView(View):

    @method_decorator(login_required())
    def post(self, request):
        if params := request.POST:
            user = request.user
            short_message = params.get("short_message")
            company = params.get("company")

            try:
                premium_request = PremiumRequest(
                    user=user,
                    short_message=short_message,
                    company=company,

                    redirected_from=params.get("redirected_from")
                )
                premium_request.save()
                messages.success(
                    request,
                    (
                        "Your request was successful. "
                        "Admin will get in touch with you for the next steps."
                    )
                )
            except Exception as e:
                messages.error(
                    request,
                    (
                        "Error: Be sure you are logged in and enter your "
                        f"company name. {e}"
                    )
                )
        return HttpResponseRedirect(reverse('users:account'))
