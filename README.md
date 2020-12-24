# LetsNote
LetsNote is a note keeping web app that lets you keep track of your notes.

## Initialization
If you're a new user, you will be required to register to the app. Existing users can simply log in.

## What can you do in LetsNote?

### CRUD on your notes
You can perform CRUD operations in this web app. That is, the user can create, read, update, and delete new or existing notes.

#### Create
The user can create new notes by simply pressing the "Add Note" button in the navbar. The user is required to add a title, some content and optional tags to distinguish the note from other notes.

#### Read
The title of the note is a hyperlink to a page where the complete contents of the note is visible.

#### Update
On the detail page, the user is provided with an edit option, where he/she can change the title, the note's content, and even the tags associated with that note.

#### Delete
The user is also provided with a delete option which will delete the note.

### Tag based search
There is a search bar on the home page which can filter your notes based on the tags associated with it. On the home page, the tags of each note are also hyperlinks which pass that tag into the search functionality.

### Profile Management
The user is provided with a profile, where he/she can change their first name, last name and email address. The user also has the option of deleting their profile, which will delete their complete account.

### Password Reset
While logging in, if the user has forgotten their password, they have the option of resetting it, by clicking the "Forgot Password?" option on the login page.

## Setting up on your system
To setup LetsNote on your system, follow the steps below.
1. Clone the repo.
```bash
git clone https://github.com/JekyllAndHyde8999/LetsNote.git
```
2. Go into the LetsNote directory.
```bash
cd LetsNote
```
3. Install dependencies
    * If you use pipenv,
    ```bash
    pipenv install
    ```
    This will create a new virtual environment and install all the dependencies.
    * If you use pip,
    ```bash
    pip install -r requirements.txt
    ```
4. Migrate and start server
```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

# API Documentation

## Base URL: http://127.0.0.1:8000/api/

### POST /api-token-auth
For a registered user to obtain their auth token<br>
**Request Format**<br>
With cURL:
```bash
curl -X POST -d '{"username": "$USERNAME", "password": "$PASSWORD"}' http://127.0.0.1:8000/api/api-token-auth/
```
With Python-Requests:
```python
requests.post(
    url="http://127.0.0.1:8000/api/api-token-auth/",
    data={
        "username": "$USERNAME",
        "password": "$PASSWORD"
    }
)
```
**Response Format**
```bash
{
    "token": "$TOKEN"
}
```
### GET /users
To get the details of the authenticated user<br>
**Request Format**<br>
With cURL:
```bash
curl -X GET -H "Authorization: Token $TOKEN" http://127.0.0.1:8000/api/users/
```
With Python-Requests:
```python
requests.get(
    url="http://127.0.0.1:8000/api/users/",
    headers={
        "Authorization": "Token $TOKEN"
    }
)
```
**Response Format**<br>
```bash
{
    "first_name": $FIRST_NAME,
    "last_name": $LAST_NAME,
    "username": $USERNAME,
    "email": $EMAIL,
    "password": $PASSWORD
}
```
*password in the above response is not the actual password, but its hash.*

### POST /users
To register as a new user<br>
**Request Format**<br>
With cURL:
```bash
curl -X POST -d '{"user": {"username": "$USERNAME", "password": "$PASSWORD", "email": "$EMAIL"}}' http://127.0.0.1:8000/api/users/
```
With Python-Requests:
```python
requests.post(
    url="http://127.0.0.1:8000/api/users/",
    data={
        "user": {
            "username": "$USERNAME",
            "password": "$PASSWORD",
            "email": "$EMAIL"
        }
    }
)
```

**Response Format**
```bash
{
    "success": "User $USERNAME created successfully.",
    "token": $TOKEN
}
```

### PUT /users
To update your email or username. (Email and username fields are unique in our database. If this API is called with an email or username that already exists in the database, the request will not be completed.)<br>
**Request Format**<br>
With cURL:
```bash
curl -X PUT -H "Authorization: Token $TOKEN" -d '{"user": {"username": "$USERNAME", "email": "$EMAIL"}}' http://127.0.0.1:8000/api/users/
```
With Python-Requests:
```python
requests.put(
    url="http://127.0.0.1:8000/api/users/",
    headers={
        "Authorization": "Token $TOKEN"
    },
    data={
        "user": {
            "username": "$USERNAME",
            "email": "$EMAIL"
        }
    }
)
```

**Response Format**
```bash
{
    "success": "User $USERNAME details updated successfully."
}
```

### DELETE /users
Calling this API will delete your entire account (including the profile and all the notes).<br>
**Request Format**<br>
With cURL:
```bash
curl -X DELETE -H "Authorization: Token $TOKEN" http://127.0.0.1:8000/api/users/
```
With Python-Requests:
```python
requests.delete(
    url="http://127.0.0.1:8000/api/users/",
    headers={
        "Authorization": "Token $TOKEN"
    },
    data={
        "note":{
            "id": $NOTE_ID
        }
    }
)
```

**Response Format**<br>
```bash
{
    "success": "User $USERNAME deleted successfully."
}
```

### GET /notes
Returns a list of all notes belonging to the authenticated user.<br>
**Request Format**<br>
With cURL:
```bash
curl -X GET -H "Authorization: Token $TOKEN" http://127.0.0.1:8000/api/notes/
```
With Python-Requests:
```python
requests.get(
    url="http://127.0.0.1:8000/api/notes/",
    headers={
        "Authorization": "Token $TOKEN"
    }
)
```
**Response Format**
```bash
[
    {
        "pk": $PK,
        "title": $TITLE,
        "note_text": $NOTE_TEXT,
        "tags": [
            $TAGS
        ],
        "last_modified": $LAST_MODIFIED
    } (for each note)
]
```

### POST /notes
To create a note belonging to the authenticated user.<br>
**Request Format**<br>
With cURL:
```bash
curl -X POST -H "Authorization: Token $TOKEN" -d '{"note": {"title": $TITLE, "note_text": $NOTE_TEXT, "tags": [$TAGS]}}' http://127.0.0.1:8000/api/notes/
```
With Python-Requests:
```python
requests.post(
    url="http://127.0.0.1:8000/api/notes/",
    headers={
        "Authorization": "Token $TOKEN"
    },
    data={
        "note": {
            "title": $TITLE,
            "note_text": $NOTE_TEXT,
            "tags": [
                $TAGS
            ]
        }
    }
)
```
**Response Format**
```bash
{
    "pk": $PK,
    "title": $TITLE,
    "note_text": $NOTE_TEXT,
    "tags": [
        $TAGS
    ],
    "last_modified": $LAST_MODIFIED
}
```
### PUT /notes
To update the content of a note (title, note_text, tags). Including all 3 fields in the request is not mandatory. Any of the fields can be updated at a time.<br>
**Request Format**<br>
With cURL:
```bash
curl -X PUT -H "Authorization: Token $TOKEN" -d '{"note": {"pk": $PK, "title": $TITLE, "note_text": $NOTE_TEXT, "tags": [$TAGS]}}' http://127.0.0.1:8000/api/notes/
```
With Python-Requests:
```python
requests.put(
    url="http://127.0.0.1:8000/api/notes/",
    headers={
        "Authorization": "Token $TOKEN"
    },
    data={
        "note": {
            "pk": $PK
            "title": $TITLE,
            "note_text": $NOTE_TEXT,
            "tags": [
                $TAGS
            ]
        }
    }
)
```
**Response Format**
```bash
{
    'success': 'Note $TITLE updated successfully'
}
```

### DELETE /notes
To delete a particular note belonging to an authenticated user.<br>
**Request Format**<br>
With cURL:
```bash
curl -X DELETE -H "Authorization: Token $TOKEN" -d '{"note": {"pk": $PK}}' http://127.0.0.1:8000/api/notes/
```
With Python-Requests:
```python
requests.delete(
    url="http://127.0.0.1:8000/api/notes/",
    headers={
        "Authorization": "Token $TOKEN"
    },
    data={
        "note": {
            "pk": $PK
        }
    }
)
```
**Response Format**
```bash
{
    'success': 'Note $TITLE deleted successfully'
}
```
