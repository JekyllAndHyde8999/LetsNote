"""LetsNote URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.authtoken import views as rest_views
from notes import views as notes_views
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', notes_views.home, name="home-page"),
    re_path('home/$', notes_views.notes_home, name="notes-home"),
    path('home/<str:tag>/', notes_views.notes_home, name="notes-home"),
    path('home/notes/<int:pk>/', notes_views.noteDetailView, name="note-detail"),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name="login"),
    path('logout/', user_views.logout_user, name='logout'),
    path('profile/<str:username>/', user_views.profile, name="profile"),
    path('deleteprofile/', user_views.deleteProfile, name='delete-profile'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name="password_reset"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name="password_reset_done"),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name="password_reset_confirm"),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name="password_reset_complete"),
    path('addnote/', notes_views.addNote, name="addnote"),
    path('deletenote/<int:pk>/', notes_views.deleteNote, name="delete-note"),
    path('editnote/<int:pk>/', notes_views.editNote, name="edit-note"),
    path('api/api-token-auth/', rest_views.obtain_auth_token),
    path('api/users/', user_views.UserAPIView.as_view()),
    path('api/notes/', notes_views.NoteAPIView.as_view()),
    path('api/tags/', notes_views.TagAPIView.as_view())
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
