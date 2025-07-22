from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import GoogleAccount

# Create your views here.

CLIENT_ID = "1037792475452-19l7nkpe7mr9uk6pmot1liussm8oegg5.apps.googleusercontent.com"
CLIENT_SECRET = "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"


def google_login(request):
    ## doing some stuff in the google auth and then getting the keys
    username = None
    email = None
    
    user = GoogleAccount(
        username=username,
        email=email,
    )
    login(user)
    return render("authentication/login.html")


def signup(request):
    pass


def logout(request):
    pass


def error_manager(request):
    pass






