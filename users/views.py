from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.response import TemplateResponse
from django.http import HttpResponseForbidden

from .serializers import UserSerializer

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.authtoken.models import Token

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


def send_welcome_mail(user, to_email):
    mail_subject = 'Welcome to LetsNote'
    message = render_to_string('users/welcome_email.html', {
        'user': user,
    })
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.send()

# Create your views here.
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            send_welcome_mail(user.username, form.cleaned_data.get('email'))
            return redirect('notes-home')
    else:
        form = UserRegisterForm()
    messages.warning(request, 'Your username cannot be changed later. Choose it wisely.')
    return render(request, 'users/register.html', {'form': form, 'title': 'Register'})


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, 'You have successfully been logged out.')
    return redirect('login')


@login_required
def profile(request, username):
    if request.user.username == username:
        if request.method == "POST":
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, 'Your profile has successfully been updated.')
                return redirect('/profile/{}'.format(request.user.username))
        else:
            u_form = UserUpdateForm(instance=request.user)
            p_form = ProfileUpdateForm(instance=request.user.profile)

        context = {
            'u_form': u_form,
            'p_form': p_form,
            'title': 'Profile'
        }
        return render(request, 'users/profile.html', context=context)
    response = TemplateResponse(request, 'notes/403.html', {})
    response.render()
    return HttpResponseForbidden(response)


@login_required
def deleteProfile(request):
    username = request.user.username
    logout(request)
    User.objects.filter(username=username).delete()
    messages.success(request, 'Account deleted!')
    return redirect('login')


class UserAPIView(APIView):
    def get(self, request):
        auth_token = request.headers.get('Authorization')
        if auth_token:
            token = Token.objects.filter(key=auth_token.split(' ')[-1])
            if token:
                user = token.first().user
                # profile = Profile.objects.get(user=user)
                user_serializer = UserSerializer(user)
                # profile_serial = ProfileSerializer(profile)
                return Response(user_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'err': 'Invalid token'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'err': 'No credentials provided'
            }, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        user = request.data.get('user')
        if not user:
            return Response({
                'err': 'No user data provided to create user'
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            assert ['email', 'password', 'username'] == sorted(user.keys())
        except:
            return Response({
                'err': f'username, password, email fields are mandatory. Received only {list(user.keys())}'
            })

        serializer = UserSerializer(data=user)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            send_welcome_mail(user.username, user.email)
            token = Token.objects.get(user=user)
            if user and token:
                return Response({
                    'success': f'User {user.username} created successfully',
                    'token': token.key
                }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        auth_token = request.headers.get('Authorization')

        if auth_token:
            token = Token.objects.filter(key=auth_token.split(' ')[-1])
            if token:
                data = request.data.get('user')
                if not data:
                    return Response({
                        'err': 'No update data provided'
                    }, status=status.HTTP_400_BAD_REQUEST)

                if "password" in data.keys():
                    return Response({
                        'err': 'Cannot update password with this API'
                    }, status=status.HTTP_406_NOT_ACCEPTABLE)

                user = token.first().user
                serializer = UserSerializer(instance=user, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    user = serializer.save()
                    return Response({
                        'success': f'User {user.username} details updated successfully.'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'err': 'Invalid token'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'err': 'No credentials provided'
            }, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request):
        auth_token = request.headers.get('Authorization')
        if auth_token:
            token = Token.objects.filter(key=auth_token.split(' ')[-1])
            if token:
                user = token.first().user
                user.delete()
                return Response({
                    'success': f'User {user.username} deleted successfully'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'err': 'Invalid token'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'err': 'No credentials provided'
            }, status=status.HTTP_401_UNAUTHORIZED)
