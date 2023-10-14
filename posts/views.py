from datetime import datetime
from functools import cached_property
from databanks.models import DataBank
from events.models import Event
import random
import re
from django.db.models import Q
from django.views.generic import (
    ListView, DetailView
)
from django.views import View
from django.conf import settings
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
)
from django.core.paginator import (
    Paginator,
    PageNotAnInteger,
    EmptyPage
)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from posts.defaults import TRENDING_THRESHOLD

from posts.models import (
    Category,
    Company,
    ReadPost,
    Region,
    Sector,
    Theme,
    Post,
    PostBody,
    Product,
)

from taggit.models import Tag
from posts.forms import ContentEditorForm, PostBodyFormset, FilterForm, WhatsInsidePostBodyForm, KeyPointPostBodyForm, \
    IntroductionPostBodyForm, ResearchAnalysisPostBodyForm, WhatWeThinkPostBodyForm
from posts.utils import get_random_obj


class IndexPostView(ListView):
    model = Post
    template_name = 'index.html'
    paginated_by = settings.PAGE_SIZE

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        posts = queryset
        context = super().get_context_data(**kwargs)

        context["featured_post"] = get_random_obj(
            self.get_queryset().filter(status=Post.PUBLISHED)
        )
        context["queryset"] = posts

        context.update(self.index_context)
        return context

    def get_queryset(self):
        search_query = self.request.GET.get("search")
        queryset = super().get_queryset()

        if search_query:
            query = (
                Q(title__icontains=search_query)
                | Q(body__icontains=search_query)
            )
            query &= Q(status=Post.PUBLISHED)
            queryset = queryset.filter(query)

        return queryset

    def get_recommended_posts(self):
        queryset = super().get_queryset().filter(status=Post.PUBLISHED)

        returning_user = False

        # get viewed posts and convert to a list
        previously_viewed_posts = self.request.COOKIES.get('viewed_posts')
        if previously_viewed_posts:
            returning_user = True
            previously_viewed_posts = [
                int(i)
                for i in previously_viewed_posts.split('-')
                if i
            ]
            # get associated tags and filter  out posts with similar tags
            interests = [
                post.tags.all()
                for post in Post.objects.filter(
                    id__in=previously_viewed_posts
                )
            ]
            interests = [tag.id for sublist in interests for tag in sublist]

            if interests:
                queryset = queryset.filter(tags__in=interests).distinct()[:8]

        return queryset if returning_user else queryset.none()
    
    @property
    def index_context(self):
        """Extra context for the our index page"""
        sectors = Post.objects.filter(
            sectors__isnull=False,
            status=Post.PUBLISHED
        ).order_by("-published_at")
        events = Event.objects.filter(status=Event.PUBLISHED)
        databanks = DataBank.objects.filter(
            status=DataBank.PUBLISHED
        ).order_by('-created_at')
        
        return {
            "trending_posts": get_random_obj(
                Post.objects.filter(
                   status=Post.PUBLISHED
                ),
                number= 3
            ),
            "featured_sector": get_random_obj(
                sectors
            ),
            "list_sectors": get_random_obj(
                sectors,
                number=4
            ),
            "featured_event": get_random_obj(events),
            "list_events": get_random_obj(events, number=4),
            "featured_databank": get_random_obj(databanks),
            "list_databanks": get_random_obj(databanks, number=2),
            "featured_insights": get_random_obj(Post.objects.filter(
                status=Post.PUBLISHED
            ), 2)
            
        }


class SinglePostView(DetailView):
    model = Post
    template_name = "posts/details.html"
    context_object_name = "post"
    slug_url_kwarg = 'slug'

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        # Get or initialize the cookie
        cookies = self.request.COOKIES
        viewed_posts = cookies.get('viewed_posts', "")

        # Add the current post to the cookie if not already added
        current_post_id = str(context['object'].id)
        if current_post_id not in viewed_posts:
            viewed_posts += f"{current_post_id}-"

        # set read post
        if self.request.user.is_authenticated:
            readpost, _ = ReadPost.objects.get_or_create(
                user=self.request.user,
                post=self.get_object()
            )
            readpost.total_posts = Post.objects.count()
            readpost.save()

        # Update cookie
        response.set_cookie('viewed_posts', viewed_posts)
        return response


class PostCategoryListView(ListView):
    '''
    List View to filter posts by Category and Subcategory

    pattern - <host>?category_name=subcat_name&category_name=subcat_name
    sample request - <host>?products=milk&products=honey&sector=money
    '''
    queryset = Post.objects.prefetch_related('subcategories').all()
    template_name = 'posts/category_list.html'
    context_object_name = "posts"
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        categories = Category.objects.values_list('name', flat=True)

        for category in self.request.GET:
            if category in categories:
                sub_cats = self.request.GET.getlist(category)
                queryset = queryset.filter(
                    subcategories__name__in=sub_cats,
                    subcategories__category__name=category
                )

        return queryset


class PostListView(ListView):
    """ should be admin only"""
    template_name = 'posts/post_list.html'
    paginated_by = 25

    def get_context_data(self, **kwargs):
        all_posts = self.get_queryset()

        paginator = Paginator(all_posts, self.paginated_by)
        page = self.request.GET.get('page')
        try:
            latest_posts = paginator.page(page)
        except PageNotAnInteger:
            latest_posts = paginator.page(1)
        except EmptyPage:
            latest_posts = paginator.page(paginator.num_pages)

        context = super(PostListView, self).get_context_data(**kwargs)
        context['form'] = FilterForm()
        context['posts'] = latest_posts
        return context

    def get_queryset(self):
        queryset = Post.objects.all()
        filters = self.request.GET
        # filter by published date
        # Get the start and end date from the query_params
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')

        if start_date and end_date:
            queryset = queryset.filter(
                published_at__range=(start_date, end_date)
            )
        else:
            if start_date and not end_date:
                queryset = queryset.filter(
                    published_at__gte=start_date
                )
            if end_date and not start_date:
                queryset = queryset.filter(
                    published_at__lte=end_date
                )

        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])
        if filters.get('subcategory'):
            queryset = queryset.filter(subcategories__in=filters["subcategory"])
        if filters.get('search'):
            queryset = queryset.filter(Q(title__icontains=filters["search"]) | Q(body__icontains=filters["search"]))
        return queryset


class ContentEditorView(View):
    template = 'posts/content_editor.html'
    form_class = ContentEditorForm
    formset_class = PostBodyFormset
    whats_inside_form = WhatsInsidePostBodyForm
    key_point_form = KeyPointPostBodyForm
    introduction_form = IntroductionPostBodyForm
    research_analysis_form = ResearchAnalysisPostBodyForm
    what_we_think_form = WhatWeThinkPostBodyForm

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        formset = self.formset_class(queryset=PostBody.objects.none())

        context = {
            'form': form,
            'formset': formset,
            'whats_inside_form': self.whats_inside_form(),
            'key_point_form': self.key_point_form(),
            'introduction_form': self.introduction_form(),
            'research_analysis_form': self.research_analysis_form(),
            'what_we_think_form': self.what_we_think_form()
        }
        return render(request, template_name=self.template, context=context)

    def post(self, request):
        form = self.form_class(data=request.POST, files=request.FILES)
        formset = self.formset_class(data=request.POST)  # add queryset if updating
        whats_inside_form = self.whats_inside_form(data=request.POST)
        key_point_form = self.key_point_form(data=request.POST)
        introduction_form = self.introduction_form(data=request.POST)
        research_analysis_form = self.research_analysis_form(data=request.POST)
        what_we_think_form = self.what_we_think_form(data=request.POST)

        all_forms = [form.is_valid(), whats_inside_form.is_valid(), key_point_form.is_valid(),
            introduction_form.is_valid(), research_analysis_form.is_valid(), what_we_think_form.is_valid() ]
        
        if all(all_forms):
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()

            whats_inside_post = whats_inside_form.save(commit=False)
            whats_inside_post.post = post
            whats_inside_post.save()

            key_point_post = key_point_form.save(commit=False)
            key_point_post.post = post
            key_point_post.save()

            introduction_post = introduction_form.save(commit=False)
            introduction_post.post = post
            introduction_post.save()
                
            research_analysis_post = research_analysis_form.save(commit=False)
            research_analysis_post.post = post
            research_analysis_post.save()

            what_we_think_post = what_we_think_form.save(commit=False)
            what_we_think_post.post = post
            what_we_think_post.save()

            if formset.is_valid():
                for form in formset:
                    postbody = form.save(commit=False)
                    postbody.post = post
                    postbody.save()

            messages.success(request, 'Post created successfully')
            return redirect('post-list')

        context = {
            'form': form,
            'formset': formset,
            'whats_inside_form': whats_inside_form,
            'key_point_form': key_point_form,
            'introduction_form': introduction_form,
            'research_analysis_form': research_analysis_form,
            'what_we_think_form': what_we_think_form,
        }
        messages.warning(request, 'Please fill the required fields below')
        return render(request, self.template, context)


class ContentUpdateView(View):
    template = 'posts/content_update.html'
    form_class = ContentEditorForm
    formset_class = PostBodyFormset

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, id=None):
        post = get_object_or_404(Post, id=id)
        form = self.form_class(instance=post)
        formset = self.formset_class(queryset=post.sections.all())

        context = {
            'form': form,
            'formset': formset,
            'post': post,
        }
        return render(request, template_name=self.template, context=context)

    def post(self, request, id=None):
        post = get_object_or_404(Post, id=id)
        form = self.form_class(
            instance=post,
            data=request.POST,
            files=request.FILES
        )
        formset = self.formset_class(
            data=request.POST,
            queryset=post.sections.all()
        )

        if all([formset.is_valid(), form.is_valid()]):
            updated_post = form.save(commit=False)
            updated_post.author = request.user
            updated_post.save()
            form.save_m2m()

            for form in formset:
                postbody = form.save(commit=False)
                postbody.post = updated_post
                postbody.save()

            messages.success(request, 'Post updated successfully')
            return redirect('post-list')

        context = {
            'form': form,
            'formset': formset,
            'post': post
        }
        messages.warning(request, 'Please correct the errors below')
        return render(request, self.template, context)


class AllResearchView(ListView):
    template_name = "posts/all_research.html"
    paginated_by = 25

    def get_context_data(self, **kwargs):
        all_posts = self.get_queryset()
        tags = Tag.objects.distinct()

        paginator = Paginator(all_posts, self.paginated_by)
        page = self.request.GET.get('page')
        try:
            all_posts = paginator.page(page)
        except PageNotAnInteger:
            all_posts = paginator.page(1)
        except EmptyPage:
            all_posts = paginator.page(paginator.num_pages)

        context = super(AllResearchView, self).get_context_data(**kwargs)
        context['all_posts'] = all_posts
        context['tags'] = tags
        context.update(self.extra_context)
        
        return context

    @cached_property
    def extra_context(self):
        return {
            'themes': Theme.objects.all(),
            'products': Product.objects.filter(),
            'regions': Region.objects.filter(),
            'sectors': Sector.objects.filter(),
            'companies': Company.objects.filter(),
            'tags': Tag.objects.filter(),
        }

    def get_queryset(self):
        queryset = Post.objects.all()
        query = Q(status=Post.PUBLISHED)
        
        if settings.USE_ADVANCE_SEARCH_QUERY:
            try:
                return self.build_advance_query_with_pg(
                    queryset, query=query
                )
            except Exception as e:
                messages.warning(
                    self.request,
                    f"Error encountered: {e}. Defaulting to basic search"
                )
                return self.build_advance_query(queryset, query)
        return self.build_advance_query(queryset, query)
        
    
    def build_advance_query_with_pg(self, queryset, query=None):
        query_params = self.request.GET
        # Perform initial search if the user is searching from the advanced
        # searching from the advanced search form
        q = query_params.get('q', '')
        
        if q:
            q = SearchQuery(q)
            query &= Q(title__search=q) | Q(body__search=q)
        
        if query_params:
            queryset = queryset.annotate(
                search=SearchVector('body', 'tags__name', 'title')
            ).filter(search=query)
        if query_params.get('tag'):
            query &= Q(tags__in=[query_params.get('tag')])
        return queryset.filter(query).order_by('-published_at')

    def normalized_text(self, text):
        return re.sub('[^\w]', '', text)
    
    def build_advance_query(self, queryset, query=None):
        query_params = self.request.GET
        # Perform initial search if the user is searching from the advanced
        # searching from the advanced search form
        q = query_params.get('q')
        if q:
            query &= Q(title__icontains=q)
            query |= Q(body__icontains=q)
            query |= Q(tags__name__icontains=q)

        if query_params.get('tag'):
            query = Q(tags__in=query_params.get('tag').split(','))
        if query_params.get('theme'):
            query |= Q(themes__in=query_params.get('theme').split(','))
        if query_params.get('product'):
            query |= Q(products__in=query_params.get('product').split(','))
        if query_params.get('sector'):
            query |= Q(sectors__in=query_params.get('sector').split(','))
        if query_params.get('region'):
            query |= Q(regions__in=query_params.get('region').split(','))
        qry = queryset.filter(query).order_by('-published_at')
        return qry
    
    def _reset_query(self, query):
        """Reset the query to the initial selection"""
        return query


class ThemesView(ListView):
    template_name = "posts/themes.html"
    paginate_by = 8
    queryset = Post.objects.filter(
        themes__isnull=False,
        status=Post.PUBLISHED
    ).order_by("-published_at")
    context_object_name = "themes"

    def get_context_data(self, **kwargs):
        posts = self.get_queryset()
        search_query = self.request.GET.get("search")
        theme = self.request.GET.get('theme')

        if theme:
            theme_obj = Theme.objects.get(name=theme)
            posts = theme_obj.posts.all()

        if search_query:
            posts = posts.filter(
                Q(title__icontains=search_query)
                | Q(body__icontains=search_query)
            )

        paginator = Paginator(posts, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            all_posts = paginator.page(page)
        except PageNotAnInteger:
            all_posts = paginator.page(1)
        except EmptyPage:
            all_posts = paginator.page(paginator.num_pages)

        context = super(ThemesView, self).get_context_data(**kwargs)
        context['posts'] = all_posts
        context["themes"] = Theme.objects.all().order_by('name')
        context['featured'] = get_random_obj(all_posts)
        return context


class SectorListView(ListView):
    template_name = "posts/sectors.html"
    paginate_by = 8
    queryset = Post.objects.filter(
        sectors__isnull=False,
        status=Post.PUBLISHED
    ).order_by("-published_at")

    def get_context_data(self, **kwargs):
        queryset = super().get_queryset()
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get("search")
        sector = self.request.GET.get('sector')

        if sector:
            sector_obj = Sector.objects.get(name=sector)
            queryset = sector_obj.posts.all()

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(body__icontains=search_query)
            )

        paginator = Paginator(queryset, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            all_posts = paginator.page(page)
        except PageNotAnInteger:
            all_posts = paginator.page(1)
        except EmptyPage:
            all_posts = paginator.page(paginator.num_pages)

        context['posts'] = all_posts
        context["sectors"] = Sector.objects.all().order_by('name')
        context['featured'] = get_random_obj(all_posts)
        return context


class BulkDeletePostsView(View):

    def get(self, request):
        posts_ids = request.GET.get('posts')
        id_list = [int(p) for p in posts_ids.split(',')]
        Post.objects.filter(id__in=id_list).delete()

        messages.success(request, 'Posts Deleted Succesfully')
        return redirect('post-list')


class BulkActionView(View):

    def get(self, request):
        posts_ids = request.GET.get('posts')
        id_list = [int(p) for p in posts_ids.split(',')]
        action = request.GET.get('action')

        if action == 'publish':
            Post.objects.filter(id__in=id_list).update(status=Post.PUBLISHED)
            messages.success(request, f'{len(id_list)} Post(s) Succesfully Published')
        elif action == 'unpublish':
            Post.objects.filter(id__in=id_list).update(status=Post.DRAFT)
            messages.success(request, f'{len(id_list)} Post(s) Succesfully Unpublished')
        elif action == 'delete':
            Post.objects.filter(id__in=id_list).delete()
            messages.success(
                request,
                (
                    f'{len(id_list)} Post(s) received a soft delete. '
                    'After 30 days, they will be permanently deleted.'
                )
            )
        return redirect('post-list')