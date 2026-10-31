from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib import messages
from django.db.models import Count
from django.db import transaction
from django.conf import settings
from core.models import *
from .models import *

User = get_user_model()


def profile(request, profile_slug):
    user = get_object_or_404(User, slug=profile_slug)
    courses = (
        Course.objects.annotate(students_filter=Count("students"))
        .filter(instructor=user)
        .prefetch_related("categories", "reviews", "students")
        .order_by("-students_filter")
    )[:4]
    events = Event.objects.filter(speakers=user)[:3]
    blogs = (Blog.objects.filter(author=user).prefetch_related("tags"))[:3]

    context = {"user": user, "courses": courses, "events": events, "blogs": blogs}
    return render(request, "accounts/profile.html", context)


def instructor_courses(request, instructor_slug):
    user = get_object_or_404(User, slug=instructor_slug)
    courses = Course.objects.filter(instructor=user).prefetch_related(
        "categories", "reviews", "students"
    )

    context = {"user": user, "courses": courses}
    return render(request, "accounts/instructor_courses.html", context)


def speaker_events(request, speaker_slug):
    user = get_object_or_404(User, slug=speaker_slug)
    events = Event.objects.filter(speakers=user)

    return render(
        request, "accounts/speaker_events.html", {"user": user, "events": events}
    )


def author_blogs(request, author_slug):
    user = get_object_or_404(User, slug=author_slug)
    blogs = Blog.objects.filter(author=user).prefetch_related("tags")

    return render(request, "accounts/author_blogs.html", {"user": user, "blogs": blogs})


def contact(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        subject = request.POST["subject"]
        message = request.POST["message"]
        try:
            with transaction.atomic():
                Contact.objects.create(
                    name=name,
                    subject=subject,
                    message=message,
                    email=email,
                )
                transaction.on_commit(
                    lambda: send_mail(
                        subject=subject,
                        message=f"Name: {name} \n Message: {message}",
                        from_email=email,
                        recipient_list=[settings.EMAIL_HOST_USER],
                        fail_silently=False,
                    )
                )
                return redirect("contact")
        except:
            messages.error(request, "Something went wrong. please try again")

    return render(request, "accounts/contact.html")


@login_required
def newsletter(request):
    if request.method == "POST":
        email = request.POST["email"]
        useremail = request.user.email
        if NewsLetter.objects.filter(useremail=useremail).exists():
            messages.warning(request, "You already Subscribed")
            return redirect(request.META.get("HTTP_REFERER"))
        with transaction.atomic():
            NewsLetter.objects.create(email=email, useremail=useremail)
            transaction.on_commit(
                lambda: send_mail(
                    subject="Welcome To Our Newsletter",
                    message=f"Hey {request.user.username} \n  You Will Be Able to See Our Latest Updates, Enjoy",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
            )
            return redirect(request.META.get("HTTP_REFERER"))

    return render(request, "accounts/newsletter.html")
