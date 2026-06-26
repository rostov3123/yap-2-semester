from django.shortcuts import render
from .data import AUTHORS, COURSES

def index(request):
    return render(request, "catalog/index.html", {"courses": COURSES[:3]})

def courses(request):
    return render(request, "catalog/courses.html", {"courses": COURSES})

def course_detail(request, slug):
    course = next((item for item in COURSES if item["slug"] == slug), None)
    return render(request, "catalog/course_detail.html" if course else "catalog/not_found.html", {"course": course})

def authors(request):
    return render(request, "catalog/authors.html", {"authors": AUTHORS})

def author_detail(request, slug):
    author = next((item for item in AUTHORS if item["slug"] == slug), None)
    author_courses = [course for course in COURSES if course["author"] == slug]
    return render(request, "catalog/author_detail.html" if author else "catalog/not_found.html", {"author": author, "courses": author_courses})

def info(request, section="about"):
    return render(request, "catalog/info.html", {"section": section})
