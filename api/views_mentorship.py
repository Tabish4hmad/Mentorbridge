from django.db.models import Q
from django.http import JsonResponse

from .models import MentorMessage, MentorshipRequest, Profile
from .view_helpers import json_body, mentor_payload, request_payload, require_role


def search_mentors(request):
    role_error = require_role(request, "student")
    if role_error:
        return role_error
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "GET required."}, status=405)

    name_tokens = [token.strip() for token in request.GET.get("name", "").split() if token.strip()]
    expertise_tokens = [
        token.strip()
        for chunk in request.GET.get("expertise", "").split(",")
        for token in chunk.split()
        if token.strip()
    ]

    mentors = Profile.objects.select_related("user").filter(role="mentor")
    for token in name_tokens:
        mentors = mentors.filter(
            Q(user__first_name__icontains=token)
            | Q(user__last_name__icontains=token)
            | Q(user__username__icontains=token)
        )
    for token in expertise_tokens:
        mentors = mentors.filter(expertise__icontains=token)

    mentors = mentors.order_by("user__first_name", "user__last_name")[:5]
    return JsonResponse({"ok": True, "mentors": [mentor_payload(profile) for profile in mentors]})


def mentor_detail(request, mentor_id):
    role_error = require_role(request, "student")
    if role_error:
        return role_error
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "GET required."}, status=405)

    mentor_profile = Profile.objects.select_related("user").filter(
        user_id=mentor_id,
        role="mentor",
    ).first()
    if not mentor_profile:
        return JsonResponse({"ok": False, "error": "Mentor not found."}, status=404)

    return JsonResponse({"ok": True, "mentor": mentor_payload(mentor_profile)})


def create_mentorship_request(request):
    role_error = require_role(request, "student")
    if role_error:
        return role_error
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    data = json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "error": "Invalid JSON."}, status=400)

    mentor_id = data.get("mentorId")
    topic = str(data.get("topic", "")).strip()
    message = str(data.get("message", "")).strip()
    mentor_profile = Profile.objects.select_related("user").filter(
        user_id=mentor_id,
        role="mentor",
    ).first()
    if not mentor_profile:
        return JsonResponse({"ok": False, "error": "Mentor not found."}, status=404)

    request_obj, created = MentorshipRequest.objects.get_or_create(
        student=request.user,
        mentor=mentor_profile.user,
        status="pending",
        defaults={
            "topic": topic or mentor_profile.expertise or "Mentorship",
            "message": message,
        },
    )
    if not created:
        return JsonResponse({"ok": False, "error": "You already have a pending request for this mentor."}, status=409)

    return JsonResponse({"ok": True, "request": request_payload(request_obj)}, status=201)


def update_mentorship_request(request, request_id):
    role_error = require_role(request, "mentor")
    if role_error:
        return role_error
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    data = json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "error": "Invalid JSON."}, status=400)

    action = str(data.get("action", "")).strip()
    if action not in {"accept", "decline"}:
        return JsonResponse({"ok": False, "error": "Choose accept or decline."}, status=400)

    request_obj = MentorshipRequest.objects.select_related("student", "student__profile", "mentor", "mentor__profile").filter(
        id=request_id,
        mentor=request.user,
        status="pending",
    ).first()
    if not request_obj:
        return JsonResponse({"ok": False, "error": "Pending request not found."}, status=404)

    request_obj.status = "accepted" if action == "accept" else "declined"
    request_obj.save(update_fields=["status", "updated_at"])
    return JsonResponse({"ok": True, "request": request_payload(request_obj)})


def send_student_message(request):
    role_error = require_role(request, "mentor")
    if role_error:
        return role_error
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    data = json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "error": "Invalid JSON."}, status=400)

    student_id = data.get("studentId")
    message = str(data.get("message", "")).strip()
    if not message:
        return JsonResponse({"ok": False, "error": "Write a short follow-up message."}, status=400)
    if len(message) > 500:
        return JsonResponse({"ok": False, "error": "Message must be 500 characters or fewer."}, status=400)

    connection = MentorshipRequest.objects.select_related("student", "student__profile").filter(
        mentor=request.user,
        student_id=student_id,
        status="accepted",
    ).first()
    if not connection:
        return JsonResponse({"ok": False, "error": "Connected student not found."}, status=404)

    mentor_message = MentorMessage.objects.create(
        mentor=request.user,
        student=connection.student,
        message=message,
    )
    return JsonResponse(
        {
            "ok": True,
            "message": {
                "id": mentor_message.id,
                "text": mentor_message.message,
                "studentName": connection.student.get_full_name() or connection.student.username,
                "createdAt": mentor_message.created_at.strftime("%b %d, %Y"),
            },
        },
        status=201,
    )
