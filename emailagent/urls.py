"""
URL configuration for emailagent project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.home_page, name="home"),
    path('admin/', admin.site.urls),
    path('authentication/', include('authentication.urls')),
    path('accounts/', include('allauth.urls')),
    path('agents/', include('agentsworkflow.urls')),
    path("get_mail/<int:message_id>/<int:user_id>", views.get_mail, name="get_mail"),
    path("send_mail", views.send_message, name="send_mail"),
    path("reply_mail/<int:message_id>/<int:thread_id>", views.reply_to_mails, name="reply_mail"),
    path("get_inbox",views.load_inbox, name="get_inbox"),
    path("get_indivisual_mail/<int:message_id>", views.get_indivisual_mail, name="get_indivisual_message"),
    path("generate_agents_respnse/<int:message_id>", views.review_agents_response, name="generate_agents_response"),
    path("reply_to_mails/<str:message_id>/<str:thread_id>", views.reply_to_mails, name="reply_to_mails"),
    path("get_replies/", views.get_replies, name="get_replies"),
    path("delete_sent_mails/<str:message_id>", views.delete_sent_mails, name="delete_sent_mails"),
    path('ask-agent/', views.query_view, name='ask-agent'),
    path('agent_chat_response/', views.agent_chat_response, name='agent-chat-response'),

]
