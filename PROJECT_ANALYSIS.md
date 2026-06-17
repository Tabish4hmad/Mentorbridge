# MentorBridge Project Analysis

## 1. Project Overview

MentorBridge is a Django-based mentorship platform where students can find mentors, send mentorship requests, and access learning notes shared by mentors. Mentors can review incoming student requests, accept or decline them, manage basic dashboard activity, and upload notes/documents for the technology they teach.

The project currently focuses on the core mentorship flow:

- User signup and login
- Role-based dashboards for students and mentors
- Student-to-mentor request flow
- Mentor request approval flow
- Mentor notes creation
- Mentor document upload
- Student access to matching notes/documents

## 2. Work Completed Till Now

### Authentication And Profiles

The app supports user registration and login using Django's built-in `User` model.

Each user also gets a `Profile` record that stores:

- Role: `student` or `mentor`
- Mentor expertise
- Avatar initials

Role-based redirects are used so students and mentors see the correct dashboard.

### Student Dashboard

The student dashboard currently includes:

- Student profile summary
- Recommended mentors
- Find mentors section
- Mentorship request list
- Connected mentor/session UI
- Notes section for matching tech topics

Students can send mentorship requests to mentors. The topic is usually based on the mentor's expertise.

### Mentor Dashboard

The mentor dashboard currently includes:

- Mentor profile summary
- Incoming student requests
- Accept/decline request actions
- Active students list
- Availability UI
- Notes section
- Document upload support for notes

Mentors can accept or decline pending requests. Accepted students appear in the active student area.

### Mentorship Request System

The `MentorshipRequest` model stores the connection request between a student and mentor.

It includes:

- Student
- Mentor
- Topic
- Message
- Status: pending, accepted, declined, cancelled
- Created and updated timestamps

The app prevents duplicate pending requests between the same student and mentor.

### Mentor Notes Feature

A `MentorNote` model was added so mentors can create learning notes for a specific tech/topic.

It includes:

- Mentor
- Tech/topic
- Title
- Optional text content
- Optional uploaded document
- Created timestamp

Students see matching notes when the note tech matches their requested mentorship topic or the mentor's expertise.

### Document Upload Feature

Mentors can now upload documents with notes.

Supported document types:

- PDF
- Word: `.doc`, `.docx`
- PowerPoint: `.ppt`, `.pptx`
- Text: `.txt`

Current file size limit:

- 10 MB

Uploaded files are stored in:

```text
media/mentor_notes/
```

In development, Django serves uploaded media through `MEDIA_URL` and `MEDIA_ROOT`.

## 3. Tech Stack Breakdown

### Backend

- Python
- Django
- Django ORM
- Django templates
- Django authentication system

The backend handles authentication, database models, page rendering, and JSON/form endpoints.

### Database

The settings are configured for PostgreSQL:

```text
ENGINE: django.db.backends.postgresql
```

The project also contains a local `db.sqlite3` file, but the current settings point to PostgreSQL using environment variables.

Important environment variables:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

### Frontend

The frontend is currently built with:

- Django templates
- Plain HTML
- CSS
- Vanilla JavaScript
- Font Awesome icons
- Google Fonts

There is no React/Vue frontend yet. Most dashboard actions use `fetch()` calls to Django endpoints.

### Static And Media Files

Static files:

```text
api/static/api/
```

Templates:

```text
api/templates/
```

Uploaded media:

```text
media/
```

## 4. Current Main Files

### Backend Core

- `backend/settings.py`
- `backend/urls.py`
- `manage.py`

### API App

- `api/models.py`
- `api/views.py`
- `api/urls.py`
- `api/admin.py`

### Templates

- `api/templates/index.html`
- `api/templates/student_dashboard.html`
- `api/templates/mentor_dashboard.html`

### CSS

- `api/static/api/student_dashboard.css`
- `api/static/api/mentor_dashboard.css`

### Migrations

- `api/migrations/0001_initial.py`
- `api/migrations/0002_mentorshiprequest.py`
- `api/migrations/0003_mentornote.py`
- `api/migrations/0004_mentornote_document_alter_mentornote_content.py`

## 5. Current API Endpoints

```text
GET  /api/health/
POST /api/auth/signup/
POST /api/auth/login/
POST /api/requests/
POST /api/requests/<request_id>/
POST /api/notes/
```

Endpoint purpose:

- `/api/health/`: Basic health check
- `/api/auth/signup/`: Register student or mentor
- `/api/auth/login/`: Login existing user
- `/api/requests/`: Student creates mentorship request
- `/api/requests/<request_id>/`: Mentor accepts or declines request
- `/api/notes/`: Mentor creates note and optionally uploads a document

## 6. Development Process Used So Far

The project is being built in small feature steps:

1. Build the base Django app.
2. Add authentication and profile roles.
3. Create separate student and mentor dashboards.
4. Add mentorship request model and request endpoints.
5. Connect dashboard buttons to backend APIs using JavaScript `fetch()`.
6. Add mentor notes model.
7. Show relevant notes to students based on requested tech.
8. Extend notes to support document uploads.
9. Run migrations after model changes.
10. Run `python manage.py check` to verify Django configuration.
11. Restart the development server and test basic response.

This process is good because it keeps each feature small, testable, and easy to debug.

## 7. Current Limitations

### Security

Some API views use `@csrf_exempt`. This is acceptable for quick development, but should be improved before production.

Recommended improvement:

- Use Django CSRF tokens in frontend requests.
- Remove unnecessary `@csrf_exempt`.

### File Upload Access

Uploaded documents are available through media URLs in development. There is no permission check on individual file downloads yet.

Recommended improvement:

- Add protected download views.
- Only allow students with related mentorship requests to access matching documents.

### Dashboard Data

Some dashboard values and rows are still static/demo data.

Examples:

- Session counts
- Availability slots
- Sample students
- Sample sessions

Recommended improvement:

- Create real models for availability and sessions.
- Remove hardcoded dashboard demo rows.

### Notes Matching Logic

Current matching is based on exact tech/topic comparison.

Recommended improvement:

- Use normalized technology tags.
- Support multiple tags per note.
- Add search and filters.

### Testing

There are not enough automated tests yet.

Recommended improvement:

- Add tests for signup/login.
- Add tests for mentorship requests.
- Add tests for notes and document uploads.
- Add permission tests for student/mentor actions.

## 8. Suggested Next Features

### 1. Protected Document Downloads

Currently, documents are linked directly through media URLs.

A better production-ready flow:

- Store uploaded file normally.
- Create a Django view like `/notes/<id>/download/`.
- Check whether the logged-in user is allowed to access the note.
- Return the file only if access is valid.

Priority: High

### 2. Availability Model

Mentors currently have a UI for adding availability, but it is not saved permanently.

Create a model:

```text
MentorAvailability
- mentor
- day
- start_time
- duration_minutes
- meeting_type
```

Priority: High

### 3. Session Booking

Students should be able to book sessions with accepted mentors.

Create a model:

```text
MentorshipSession
- student
- mentor
- topic
- scheduled_at
- duration_minutes
- status
```

Priority: High

### 4. Student Learning Goals

Students should be able to define what tech they are learning.

Possible fields:

- Current tech
- Skill level
- Goal
- Weekly availability
- Preferred mentor style

Priority: Medium

### 5. Tech Tags

Instead of using plain text expertise and topic matching, introduce a proper `TechTag` model.

Possible model:

```text
TechTag
- name
- slug
```

Then connect tags to:

- Mentor profiles
- Mentorship requests
- Mentor notes
- Student goals

Priority: Medium

### 6. Notes Search And Filter

Students should be able to:

- Search notes by title
- Filter by tech
- Filter by mentor
- Filter by file type

Priority: Medium

### 7. Mentor Note Management

Mentors should be able to:

- Edit notes
- Delete notes
- Replace uploaded documents
- See which students can access each note

Priority: Medium

### 8. Notifications

Add notifications for:

- Request sent
- Request accepted
- Request declined
- New note uploaded
- Session booked

Priority: Medium

### 9. Admin Improvements

Django admin can be improved with:

- Search fields
- Filters
- List displays
- Better note and request management

Priority: Low

### 10. UI Polish

Possible UI improvements:

- Better empty states
- Loading states on buttons
- Form validation messages
- Mobile dashboard refinements
- Remove static/demo dashboard data

Priority: Medium

## 9. Recommended Next Development Order

The best next sequence is:

1. Protect uploaded document downloads.
2. Add real mentor availability model.
3. Add session booking model.
4. Replace demo dashboard data with database data.
5. Add edit/delete support for mentor notes.
6. Add student learning goals.
7. Add tech tags for cleaner matching.
8. Add notifications.
9. Add automated tests.
10. Polish UI and prepare for deployment.

## 10. Commands Used In Development

Create migrations:

```powershell
python manage.py makemigrations api
```

Apply migrations:

```powershell
python manage.py migrate
```

Run Django checks:

```powershell
python manage.py check
```

Start server:

```powershell
python manage.py runserver 127.0.0.1:8000
```

## 11. Summary

The project now has a strong base for a mentorship platform. The most important completed flows are user roles, dashboards, mentorship requests, mentor-created notes, and document uploads.

The next major step should be making the platform more data-driven by adding real availability and session booking models. After that, protected document access, better matching, notifications, and tests will make the app more complete and production-ready.
