from django import template

import readtime

register = template.Library()


@register.filter
def get_dict_values(dict_collections, key, default=''):
    return dict_collections[key]


@register.inclusion_tag('_pagination.html')
def render_paginator(object_list, page_tag="page"):
    return {'object_list': object_list, 'page_tag': page_tag}


@register.inclusion_tag('_post_tag.html')
def render_post(post):
    return {'post': post}


@register.filter
def get_readtime(post):
    post_sections = post.sections.all()
    readables = post.title
    readables += ''.join([x for x in post_sections.values_list('text', flat=True) if x])
    readables += ''.join([x for x in post_sections.values_list('title', flat=True) if x])
    result = readtime.of_text(readables)
    return result.text


@register.inclusion_tag('_jumbo.html')
def render_featured_post(object_list):
    return {'object_list': object_list}


@register.inclusion_tag('_header.html')
def render_header(object_list):
    return {'object_list': object_list}


@register.inclusion_tag('_vertical_post_tag.html')
def render_vertical_post(post):
    return {'post': post}