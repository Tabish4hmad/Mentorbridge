from django.urls import path

from .views import (
    chat_thread_messages,
    chat_threads,
    create_note,
    create_mentorship_request,
    download_note_document,
    health_check,
    login_user,
    logout_user,
    mentor_detail,
    search_mentors,
    send_student_message,
    signup_user,
    update_profile_avatar,
    update_profile_info,
    update_mentorship_request,
)


urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("auth/signup/", signup_user, name="signup-user"),
    path("auth/login/", login_user, name="login-user"),
    path("auth/logout/", logout_user, name="logout-user"),
    path("profile/basic-info/", update_profile_info, name="update-profile-info"),
    path("profile/avatar/", update_profile_avatar, name="update-profile-avatar"),
    path("mentors/search/", search_mentors, name="search-mentors"),
    path("mentors/<int:mentor_id>/", mentor_detail, name="mentor-detail"),
    path("requests/", create_mentorship_request, name="create-mentorship-request"),
    path("requests/<int:request_id>/", update_mentorship_request, name="update-mentorship-request"),
    path("messages/", send_student_message, name="send-student-message"),
    path("inbox/threads/", chat_threads, name="chat-threads"),
    path("inbox/threads/<int:thread_id>/messages/", chat_thread_messages, name="chat-thread-messages"),
    path("notes/", create_note, name="create-note"),
    path("notes/<int:note_id>/download/", download_note_document, name="download-note-document"),
]
