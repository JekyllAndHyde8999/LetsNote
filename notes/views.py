from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponseForbidden

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.authtoken.models import Token

from .serializers import NoteSerializer, TagSerializer
from .models import Notes, Note_Tag
from .forms import NoteForm

# User defined objects here.

shorten_text = lambda text: text[:27] + '...' if len(text) > 30 else text


class AbstractNote:
    def __init__(self, id, title, note_text, last_modified, tags_list):
        self.id = id
        self.title = title
        self.note_text = note_text
        self.last_modified = last_modified
        self.tags_list = tags_list


def concatTags(note_obj, as_string=False):
    note_obj_tags = Note_Tag.objects.filter(note=note_obj)
    tags_list = [tag.tag_text for tag in note_obj_tags]
    if as_string:
        return ','.join(tags_list)
    return tags_list


# Create your views here.


def home(request):
    return render(request, 'notes/home.html', {})


@login_required
def notes_home(request, tag=None):
    if tag:
        notes = sorted([tag_obj.note for tag_obj in Note_Tag.objects.filter(tag_text=tag.lower())],
                        key=lambda x: x.last_modified,
                        reverse=True)
    elif request.method == "POST":
        tag = request.POST["tag-search"]
        tags = tag.lower().replace(",", " ").split()
        notes = set()
        for tag_indie in tags:
            temp = list(Note_Tag.objects.filter(tag_text=tag_indie))
            temp = list(map(lambda x: x.note, temp))
            temp = list(filter(lambda x: x.user == request.user, temp))
            notes.update(temp)
        notes = sorted(list(notes), key=lambda x: x.last_modified, reverse=True)
        if tag.lower().strip() == '':
            notes = Notes.objects.filter(user=request.user).order_by('-last_modified')
    else:
        notes = Notes.objects.filter(user=request.user).order_by('-last_modified')

    notesList = [AbstractNote(N.id, N.title, shorten_text(N.note_text), N.last_modified, concatTags(N)) for N in notes]

    context = {
        'notes': notesList,
        'userNotesExists': bool(Notes.objects.filter(user=request.user)),
        'title': 'Home',
        'existing_tag': tag.strip().lower() if tag else ''
    }
    return render(request, 'notes/notes_home.html', context=context)


@login_required
def noteDetailView(request, pk):
    note_obj = Notes.objects.filter(pk=pk).first()
    if not note_obj or note_obj.user != request.user:
        response = TemplateResponse(request, 'notes/403.html', {})
        response.render()
        return HttpResponseForbidden(response)

    tag_list = concatTags(note_obj)
    print(tag_list)
    context = {
        'note_id': note_obj.id,
        'title': note_obj.title,
        'last_modified': note_obj.last_modified,
        'note_text': note_obj.note_text,
        'tags': tag_list
    }
    return render(request, 'notes/notes_detail.html', context=context)


@login_required
def addNote(request):
    if request.method == "POST":
        tags =  request.POST["tags"]
        tags = tags.lower().replace(",", " ").split()

        note_obj = Notes(title=request.POST["title"], note_text=request.POST["note_text"], user=request.user)
        note_obj.save()

        for tag in tags:
            Note_Tag.objects.create(note=note_obj, tag_text=tag)

        messages.success(request, 'Added note successfully!')
        return redirect('notes-home')
    #messages.warning(request, 'Tags must NOT contain spaces or commas within them.')
    return render(request,'notes/addnote.html', {'title': 'Add Note'})


@login_required
def editNote(request, pk):
    pk_list = [note.id for note in request.user.notes_set.all()]
    if pk not in pk_list:
        response = TemplateResponse(request, 'notes/403.html', {})
        response.render()
        return HttpResponseForbidden(response)

    note = Notes.objects.get(pk=pk)

    if request.method == "POST":
        nf = NoteForm(request.POST, instance=note)
        tag_set = Note_Tag.objects.filter(note=note)
        tag_set.delete()

        tags =  request.POST["tags"]
        tags = tags.lower().replace(",", " ").split()

        for tag in tags:
            Note_Tag.objects.create(note=note, tag_text=tag)

        if nf.is_valid():
            nf.save()
            messages.success(request, 'Successfully updated note!')
            return redirect('notes-home')
    else:
        nf = NoteForm(instance=note)
        tags = Note_Tag.objects.filter(note=note)
    return render(request, 'notes/edit_note.html', {"form": nf, "tags": tags, "title": "Edit Note", "note_id": note.id})


@login_required
def deleteNote(request, pk):
    pk_list = [note.id for note in request.user.notes_set.all()]
    if pk not in pk_list:
        response = TemplateResponse(request, 'notes/403.html', {})
        response.render()
        return HttpResponseForbidden(response)

    Notes.objects.filter(pk=pk).delete()
    messages.success(request, 'Note has been deleted successfully.')
    return redirect('notes-home')


# API views
class NoteAPIView(APIView):
    def get(self, request):
        auth_token = request.headers.get('Authorization')
        if auth_token:
            token = Token.objects.filter(key=auth_token.split(' ')[-1])
            if token:
                user = token.first().user
                notes = Notes.objects.filter(user=user).order_by('-last_modified')
                note_serializer = NoteSerializer(notes, many=True)
                return Response(note_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'err': 'Invalid token'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'err': 'No credentials provided'
            }, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        auth_token = request.headers.get('Authorization')

        if auth_token:
            token = Token.objects.filter(key=auth_token.split(' ')[-1])
            if token:
                user = token.first().user
                note = request.data.get('note')
                note_obj = Notes.objects.create(
                            title=note.get('title'),
                            note_text=note.get('note_text'),
                            user=user
                        )
                for tag in note.get('tags'):
                    Note_Tag.objects.create(tag_text=tag, note=note_obj)

                note_serializer = NoteSerializer(note_obj)
                return Response(note_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'err': 'Invalid token'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'err': 'No credentials provided'
            }, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request):
        auth_token = request.headers.get('Authorization')

        if auth_token:
            token = Token.objects.filter(key=auth_token.split(' ')[-1])
            if token:
                user = token.first().user
                note = request.data.get('note')
                try:
                    note_obj = Notes.objects.filter(pk=note['pk'], user=user).first()
                except:
                    return Response({
                        'err': 'No note provided to update.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                if not note_obj:
                    return Response({
                        'err': 'You do not have access to this note.'
                    }, status=status.HTTP_403_FORBIDDEN)

                tag_set = Note_Tag.objects.filter(note=note_obj)
                tag_set.delete()

                note_obj.title = note.get('title', note_obj.title)
                note_obj.note_text = note.get('note_text', note_obj.note_text)
                note_obj.save()

                for tag in note.get('tags'):
                    Note_Tag.objects.create(tag_text=tag, note=note_obj)

                note_serializer = NoteSerializer(note_obj)
                return Response({
                    'success': f'Note {note_obj.title} updated successfully'
                }, status=status.HTTP_200_OK)
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
                try:
                    note = request.data['note']
                except:
                    return Response({
                        'err': 'No note provided.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                try:
                    note_obj = Notes.objects.filter(pk=note['pk'], user=user).first()
                except:
                    return Response({
                        'err': 'Note id not provided.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                if not note_obj:
                    return Response({
                        'err': 'You do not have access to this note.'
                    }, status=status.HTTP_403_FORBIDDEN)

                note_obj.delete()
                return Response({
                    'success': f'Note {note_obj.title} deleted successfully.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'err': 'Invalid token'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'err': 'No credentials provided'
            }, status=status.HTTP_401_UNAUTHORIZED)


class TagAPIView(APIView):
    def get(self, request):
        tags = Note_Tag.objects.all()
        tag_serializer = TagSerializer(tags, many=True)
        return Response(tag_serializer.data, status=status.HTTP_200_OK)
