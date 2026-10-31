from django.db import models
from django.urls import reverse
from django.conf import settings
from django.db.models import Avg
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=150)
    img = models.ImageField(upload_to="Category_Image/", null=True, blank=True)
    slug = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Course(models.Model):
    class Type(models.TextChoices):
        online = "online", "Online"
        offline = "offline", "Offline"

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructor_courses",
    )
    name = models.CharField(max_length=100, db_index=True)
    img = models.ImageField(upload_to="Course_Image/")
    price = models.PositiveIntegerField(default=1)
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="students", blank=True
    )
    lessons = models.PositiveIntegerField(default=1)
    course_type = models.CharField(max_length=20, choices=Type.choices)
    starts_on = models.DateField(auto_now_add=False, null=True, blank=True)
    ends_on = models.DateField(auto_now_add=False, null=True, blank=True)
    duration = models.PositiveIntegerField(default=0, null=True, blank=True)
    course_hours = models.PositiveIntegerField(default=0, null=True, blank=True)
    max_seats = models.PositiveIntegerField(default=0, null=True, blank=True)
    location = models.CharField(max_length=150, null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name="categories")
    overview = models.TextField()
    description_requirements = models.TextField()
    slug = models.SlugField(max_length=100, null=True, blank=True, db_index=True)

    def __str__(self):
        return self.name

    def calc_rating(self):
        reviews = Review.objects.filter(course=self).aggregate(average=Avg("rating"))
        avg = 0
        if reviews["average"] is not None:
            avg = sum(reviews["average"])
        return avg

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Event(models.Model):
    speakers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="speakers_event"
    )
    name = models.CharField(max_length=100, db_index=True)
    img = models.ImageField(upload_to="Course_Image/")
    price = models.PositiveIntegerField(default=1)
    audience = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="audience", blank=True
    )
    starts_on = models.DateField(auto_now_add=False)
    starts_at = models.TimeField(auto_now_add=False)
    ends_at = models.TimeField(auto_now_add=False)
    max_seats = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=150)
    phone = models.CharField(max_length=11)
    overview = models.TextField()
    description = models.TextField()
    slug = models.SlugField(max_length=100, null=True, blank=True, db_index=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Blog(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="author_blog",
    )
    title = models.CharField(max_length=100, db_index=True)
    img = models.ImageField(upload_to="Course_Image/")
    tags = models.ManyToManyField(Category, related_name="tags")
    saves = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="saved_blog", blank=True
    )
    loves = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="loved_blog", blank=True
    )
    content = models.TextField()
    published = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=100, null=True, blank=True, db_index=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    rating = models.PositiveIntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
