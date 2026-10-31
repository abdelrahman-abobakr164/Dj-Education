from django.shortcuts import render, redirect

# Create your views here.


def checkout(request):
    return render(request, "payment/checkout.html")
