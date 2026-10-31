from .models import Category
from django.db.models import Q
from accounts.models import NewsLetter


def share_func(request):
    if "superuser" in request.path:
        return {}
    else:
        if request.user.is_authenticated:
            check_newsletter = NewsLetter.objects.filter(useremail=request.user.email)
            if not check_newsletter.exists():
                show_newsletter = True
            else:
                show_newsletter = False
        else:
            show_newsletter = True
        categories = Category.objects.filter(Q(img__icontains=".")).prefetch_related(
            "categories", "tags"
        )[:8]
        return {"categories": categories, "show_newsletter": show_newsletter}
