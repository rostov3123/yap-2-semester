"""Представления каталога на основе констант."""
from django.http import Http404
from django.shortcuts import render
from .data import AUTHORS, COURSES


def index(request):
    return render(request, 'catalog/index.html', {'courses': COURSES})


def courses(request):
    return render(request, 'catalog/courses.html', {'courses': COURSES})


def course_detail(request, pk):
    course = next((c for c in COURSES if c['id'] == pk), None)
    if course is None:
        raise Http404('Курс не найден')
    author = next(a for a in AUTHORS if a['id'] == course['author_id'])
    return render(request, 'catalog/course_detail.html', {'course': course, 'author': author})


def authors(request):
    return render(request, 'catalog/authors.html', {'authors': AUTHORS})


def author_detail(request, pk):
    author = next((a for a in AUTHORS if a['id'] == pk), None)
    if author is None:
        raise Http404('Автор не найден')
    return render(request, 'catalog/author_details.html', {'author': author, 'courses': [c for c in COURSES if c['author_id'] == pk]})


def info(request):
    return render(request, 'catalog/info.html')


def not_found(request, exception=None):
    return render(request, 'catalog/not_found.html', status=404)


def forbidden(request, exception=None):
    return render(request, '403.html', status=403)
