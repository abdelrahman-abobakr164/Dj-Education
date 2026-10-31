from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("courses/", views.courses, name="courses"),
    path("events/", views.events, name="events"),
    path("blogs/", views.blogs, name="blogs"),
    path("search/", views.search, name="search"),
    path("my-saved-blogs/", views.saved_blogs, name="my-saved-blogs"),
    path("my-events/", views.my_events, name="my-events"),
    path("my-courses/", views.my_courses, name="my-courses"),
    path("search/<category_slug>/", views.search, name="category_slug"),
    path("course/<str:slug>/", views.course, name="course"),
    path("event/<str:slug>/", views.event, name="event"),
    path("blog/<str:slug>/", views.blog, name="blog"),
    path("save-unsave/<str:slug>/<blog_id>/", views.save_unsave, name="save-unsave"),
    path("love-unlove/<str:slug>/<blog_id>/", views.love_unlove, name="love-unlove"),
    path("comment/<str:slug>/<blog_id>/", views.comment, name="comment"),
    path("review/<course_slug>/<course_id>/", views.review, name="review"),
]
