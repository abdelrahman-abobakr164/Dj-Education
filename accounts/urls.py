from django.urls import path
from . import views

urlpatterns = [
    path("contact/", views.contact, name="contact"),
    path("newsletter/", views.newsletter, name="newsletter"),
    path("<profile_slug>/", views.profile, name="profile"),
    path(
        "<instructor_slug>/courses/",
        views.instructor_courses,
        name="instructor-courses",
    ),
    path("<speaker_slug>/events/", views.speaker_events, name="speaker-events"),
    path("<author_slug>/blogs/", views.author_blogs, name="author-blogs"),
]
