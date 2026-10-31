from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Q, Count
from django.contrib import messages
from django.db import transaction
from .models import *

User = get_user_model()


def index(request):
    courses = (
        Course.objects.annotate(students_filter=Count("students"))
        .order_by("-students_filter")
        .prefetch_related("categories", "students")[:6]
    )

    blogs = Blog.objects.all().prefetch_related("tags")[:6]
    events = Event.objects.all()[:6]

    return render(
        request,
        "core/index.html",
        {"courses": courses, "blogs": blogs, "events": events},
    )


def search(request, category_slug=None):
    if search := request.GET.get("q") or category_slug:
        courses = (
            Course.objects.annotate(students_filter=Count("students"))
            .filter(Q(name__icontains=search) | Q(categories__name__icontains=search))
            .prefetch_related("categories", "reviews", "students")
            .order_by("-students_filter")
        )
        blogs = (
            Blog.objects.annotate(loves_filter=Count("loves"))
            .filter(Q(title__icontains=search) | Q(tags__name__icontains=search))
            .prefetch_related("tags")
            .order_by("-loves_filter")
        )

        events = Event.objects.filter(name__icontains=search)

    context = {
        "courses": courses,
        "blogs": blogs,
        "events": events,
        "category_slug": category_slug,
    }
    return render(request, "core/search.html", context)


def courses(request):
    courses = (
        Course.objects.annotate(students_filter=Count("students"))
        .order_by("-students_filter")
        .prefetch_related("categories", "reviews", "students")
    )
    return render(request, "core/courses.html", {"courses": courses})


def course(request, slug):
    course = get_object_or_404(
        Course.objects.prefetch_related(
            "reviews", "categories", "students"
        ).select_related("instructor"),
        slug=slug,
    )
    reviews = Review.objects.filter(course=course).select_related("user", "course")
    related_courses = (
        Course.objects.filter(categories__in=course.categories.all())
        .prefetch_related("reviews")
        .exclude(slug=slug)[:3]
    )
    available_seats = (
        course.max_seats - course.students.all().count()
        if course.course_type == "offline"
        else None
    )

    context = {
        "course": course,
        "reviews": reviews,
        "related_courses": related_courses,
        "available_seats": available_seats,
    }
    return render(request, "core/course.html", context)


@login_required
def review(request, course_slug, course_id):
    course = Course.objects.get(slug=course_slug, id=course_id)
    if request.method == "POST":
        message = request.POST["message"]
        try:
            with transaction.atomic():
                Review.objects.update_or_create(
                    user=request.user,
                    course=course,
                    defaults={
                        "rating": request.POST["rating"],
                        "message": message,
                    },
                )
                transaction.on_commit(
                    lambda: send_mail(
                        subject="Review For Your Course",
                        message=message,
                        email=request.user.email,
                        recipient_list=[course.instructor.email],
                        fail_silently=False,
                    )
                )
                messages.success(
                    request, "Your Review has been Submitted Successfully!"
                )
                return redirect("course", course.slug)

        except:
            messages.error(request, "something Went Wrong, Please Try again")
            return redirect("course", course.slug)
    return redirect("course", course.slug)


def events(request):
    events = Event.objects.all()
    return render(request, "core/events.html", {"events": events})


def event(request, slug):
    event = get_object_or_404(
        Event.objects.prefetch_related("audience", "speakers"), slug=slug
    )
    return render(request, "core/event.html", {"event": event})


def blogs(request):
    blogs = Blog.objects.all().prefetch_related("tags")
    return render(request, "core/blogs.html", {"blogs": blogs})


def blog(request, slug):
    blog = (
        Blog.objects.prefetch_related("tags", "loves", "saves", "comments")
        .select_related("author")
        .get(slug=slug)
    )
    comments = Comment.objects.filter(blog=blog).select_related("user")
    popular_blogs = (
        Blog.objects.annotate(loved_filter=Count("loves"))
        .order_by("-loved_filter")
        .exclude(slug=slug)
    )

    context = {"comments": comments, "blog": blog, "popular_blogs": popular_blogs}
    return render(request, "core/blog.html", context)


@login_required
def save_unsave(request, slug, blog_id):
    blog = get_object_or_404(
        Blog.objects.prefetch_related("saves"), slug=slug, id=blog_id
    )
    if request.user in blog.saves.all():
        blog.saves.remove(request.user)
    else:
        blog.saves.add(request.user)
    return redirect("blog", slug=slug)


@login_required
def love_unlove(request, slug, blog_id):
    blog = get_object_or_404(
        Blog.objects.prefetch_related("loves"), slug=slug, id=blog_id
    )
    if request.user in blog.loves.all():
        blog.loves.remove(request.user)
    else:
        blog.loves.add(request.user)
    return redirect("blog", slug=slug)


@login_required
def comment(request, slug, blog_id):
    blog = Blog.objects.get(slug=slug, id=blog_id)
    if request.method == "POST":
        content = request.POST["content"]
        try:
            Comment.objects.create(user=request.user, blog=blog, content=content)
            messages.success(request, "Your Comment has been Submitted Successfully!")
            return redirect("blog", blog.slug)

        except:
            messages.error(request, "something Went Wrong, Please Try again")
            return redirect("blog", blog.slug)
    return redirect("blog", blog.slug)


def my_courses(request):
    user = get_object_or_404(User, id=request.user.id)
    courses = Course.objects.filter(students=user)
    return render(request, "core/my_courses.html", {"courses": courses})


def my_events(request):
    user = get_object_or_404(User, id=request.user.id)
    events = Event.objects.filter(audience=user)
    return render(request, "core/my_events.html", {"events": events})


def saved_blogs(request):
    user = get_object_or_404(User, id=request.user.id)
    blogs = Blog.objects.filter(saves=user).prefetch_related("tags")
    return render(request, "core/saved_blogs.html", {"blogs": blogs})
