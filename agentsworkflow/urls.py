from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('fetch_emails/<int:id>', views.fetch_emails, name='fetch_emails'),
    path('process_emails/<int:id>', views.process_emails, name='process_emails'),
]