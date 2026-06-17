import json
from pathlib import Path

from django.db.models import Q
from django.http import JsonResponse

from .models import ChatThread, MentorshipRequest


def json_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def user_payload(user):
    profile = user.profile
    return {
        "id": user.id,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "email": user.email,
        "username": user.username,
        "role": profile.role,
        "expertise": profile.expertise,
        "avatar": profile.avatar,
        "avatarUrl": profile.avatar_image.url if profile.avatar_image else "",
        "mobile": profile.mobile,
        "address": profile.address,
        "institute": profile.institute,
        "availability": profile.availability,
    }


def require_role(request, role):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "Please sign in first."}, status=401)
    if request.user.profile.role != role:
        return JsonResponse({"ok": False, "error": f"Only {role}s can do this."}, status=403)
    return None


def request_payload(mentorship_request):
    student = mentorship_request.student
    mentor = mentorship_request.mentor
    return {
        "id": mentorship_request.id,
        "status": mentorship_request.status,
        "topic": mentorship_request.topic,
        "student": {
            "id": student.id,
            "name": student.get_full_name() or student.username,
            "email": student.email,
            "avatar": student.profile.avatar,
            "avatarUrl": student.profile.avatar_image.url if student.profile.avatar_image else "",
            "mobile": student.profile.mobile,
            "institute": student.profile.institute,
            "address": student.profile.address,
        },
        "mentor": {
            "id": mentor.id,
            "name": mentor.get_full_name() or mentor.username,
            "email": mentor.email,
            "avatar": mentor.profile.avatar,
            "avatarUrl": mentor.profile.avatar_image.url if mentor.profile.avatar_image else "",
            "expertise": mentor.profile.expertise,
        },
    }


def note_payload(note):
    return {
        "id": note.id,
        "tech": note.tech,
        "title": note.title,
        "content": note.content,
        "documentUrl": f"/api/notes/{note.id}/download/" if note.document else "",
        "documentName": Path(note.document.name).name if note.document else "",
        "mentor": note.mentor.get_full_name() or note.mentor.username,
        "createdAt": note.created_at.strftime("%b %d, %Y"),
    }


def mentor_payload(profile):
    user = profile.user
    return {
        "id": user.id,
        "name": user.get_full_name() or user.username,
        "email": user.email,
        "avatar": profile.avatar or "M",
        "avatarUrl": profile.avatar_image.url if profile.avatar_image else "",
        "expertise": profile.expertise or "Mentorship",
        "institute": profile.institute or "Not set",
        "availability": profile.availability or "Not set",
    }


def can_access_note(user, note):
    if not user.is_authenticated:
        return False
    if note.mentor_id == user.id:
        return True
    if not hasattr(user, "profile") or user.profile.role != "student":
        return False

    return MentorshipRequest.objects.filter(
        student=user,
        mentor=note.mentor,
        status="accepted",
    ).filter(
        Q(topic__iexact=note.tech) | Q(mentor__profile__expertise__iexact=note.tech)
    ).exists()


def ensure_chat_threads(user):
    if not user.is_authenticated or not hasattr(user, "profile"):
        return ChatThread.objects.none()

    role = user.profile.role
    if role == "mentor":
        connections = MentorshipRequest.objects.select_related("student").filter(
            mentor=user,
            status="accepted",
        )
        for connection in connections:
            ChatThread.objects.get_or_create(mentor=user, student=connection.student)
        return ChatThread.objects.select_related("mentor", "mentor__profile", "student", "student__profile").filter(mentor=user)

    if role == "student":
        connections = MentorshipRequest.objects.select_related("mentor").filter(
            student=user,
            status="accepted",
        )
        for connection in connections:
            ChatThread.objects.get_or_create(mentor=connection.mentor, student=user)
        return ChatThread.objects.select_related("mentor", "mentor__profile", "student", "student__profile").filter(student=user)

    return ChatThread.objects.none()


def chat_partner(thread, user):
    return thread.student if user.profile.role == "mentor" else thread.mentor


def chat_thread_payload(thread, user):
    partner = chat_partner(thread, user)
    last_message = thread.messages.order_by("-created_at").first()
    return {
        "id": thread.id,
        "partnerName": partner.get_full_name() or partner.username,
        "partnerAvatar": partner.profile.avatar or partner.first_name[:1].upper() or "U",
        "partnerAvatarUrl": partner.profile.avatar_image.url if partner.profile.avatar_image else "",
        "partnerRole": partner.profile.role.title(),
        "partnerEmail": partner.email,
        "lastMessage": last_message.body if last_message else "No messages yet.",
        "lastAt": last_message.created_at.strftime("%b %d, %I:%M %p") if last_message else "",
    }


def chat_message_payload(message, user):
    return {
        "id": message.id,
        "body": message.body,
        "senderId": message.sender_id,
        "senderName": message.sender.get_full_name() or message.sender.username,
        "isMine": message.sender_id == user.id,
        "createdAt": message.created_at.strftime("%b %d, %I:%M %p"),
    }


def get_accessible_thread(user, thread_id):
    if not user.is_authenticated or not hasattr(user, "profile"):
        return None
    filters = {"id": thread_id}
    if user.profile.role == "mentor":
        filters["mentor"] = user
    elif user.profile.role == "student":
        filters["student"] = user
    else:
        return None
    return ChatThread.objects.select_related("mentor", "mentor__profile", "student", "student__profile").filter(**filters).first()
