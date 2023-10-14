from datetime import datetime
from django.views import generic
from django.urls import reverse_lazy
from django.core.paginator import (
    Paginator,
    PageNotAnInteger,
    EmptyPage
)
from django.db.models import Q

from events.models import Event
from .forms import EventForm, EventFilterForm
from posts.utils import get_random_obj, get_single_random_obj


class EventListView(generic.ListView):
    context_object_name = 'events'
    template_name = 'events/event_list_new.html'
    paginated_by = 25

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        context = super().get_context_data(**kwargs)

        _presentations_ids = [
            e.id
            for e in queryset.filter(event_type=Event.PRESENTATION)
            if e.banner_image
        ]
        _videos_ids = [
            e.id
            for e in queryset.filter(event_type=Event.VIDEO)
            if e.banner_image
        ]
        event_videos = Event.objects.filter(id__in=_videos_ids)
        event_presentations = Event.objects.filter(
            id__in=_presentations_ids
        ).order_by('id')
        # Video pagination
        video_paginator = Paginator(event_videos, self.paginated_by)
        video_page = self.request.GET.get('video_page')
        try:
            videos = video_paginator.page(video_page)
        except PageNotAnInteger:
            videos = video_paginator.page(1)
        except EmptyPage:
            videos = video_paginator.page(video_paginator.num_pages)
        # Presentation pagination
        pres_paginator = Paginator(
            event_presentations,
            self.paginated_by
        )
        pres_page = self.request.GET.get('pres_page')
        try:
            presentations = pres_paginator.page(pres_page)
        except PageNotAnInteger:
            presentations = pres_paginator.page(1)
        except EmptyPage:
            presentations = pres_paginator.page(pres_paginator.num_pages)
        context["featured"] = get_random_obj(
            [e for e in queryset if e.banner_image]
        )
        context['event_videos'] = videos
        context['event_presentations'] = presentations
        context['first_featured'] = get_single_random_obj(queryset)
        context['second_featured'] = get_single_random_obj(queryset)

        return context

    def get_queryset(self):
        queryset = Event.objects.filter(
            status=Event.PUBLISHED
        ).order_by('-created_at')
        query_params = self.request.GET
        if query_params.get('search'):
            queryset = queryset.filter(Q(title__icontains=query_params["search"]) | Q(article__icontains=query_params["search"]))
        return queryset


class EventDetailView(generic.DetailView):
    model = Event
    context_object_name = 'event'
    template_name = 'events/event_detail.html'


class EventCreateView(generic.CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_editor.html'
    success_url = reverse_lazy('event_list')


class EventAdminView(generic.ListView):
    queryset = Event.objects.all()
    context_object_name = 'events'
    paginate_by = 25
    template_name = 'events/event_admin_list.html'

    def get_context_data(self, **kwargs):
        all_events = self.get_queryset()

        paginator = Paginator(all_events, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            latest_events = paginator.page(page)
        except PageNotAnInteger:
            latest_events = paginator.page(1)
        except EmptyPage:
            latest_events = paginator.page(paginator.num_pages)

        context = super(EventAdminView, self).get_context_data(**kwargs)
        context['form'] = EventFilterForm()
        context['events'] = latest_events
        return context

    def get_queryset(self):
        queryset = Event.objects.all()
        filters = self.request.GET
        if filters.get('event_date'):
            event_date = datetime.strptime(filters['event_date'], '%Y-%m-%d')
            month = event_date.month
            year = event_date.year
            queryset = queryset.filter(
                event_date__month=month,
                event_date__year=year
            )
        if filters.get('status'):
            queryset = queryset.filter(status=filters['status'])
        if filters.get('search'):
            queryset = queryset.filter(Q(title__icontains=filters["search"]) | Q(article__icontains=filters["search"]))
        return queryset
