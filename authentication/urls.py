from django.urls import path

from . import views

urlpatterns = [
    path('login', views.google_login, name="login"),
    path('signup', views.signup, name="signup"),
    path('logout', views.logout, name='logout'),
    path('error', views.error_manager, name='error_management'),
    
]