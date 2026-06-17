from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import MentorMessage, MentorNote, MentorshipRequest, Profile


@ensure_csrf_cookie
def home(request):
    return render(request, "index.html")


@ensure_csrf_cookie
def student_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("/")

    profile = request.user.profile
    if profile.role != "student":
        return redirect("/")

    mentors = Profile.objects.select_related("user").filter(role="mentor").order_by("user__first_name")
    requests = MentorshipRequest.objects.select_related("mentor", "mentor__profile").filter(
        student=request.user,
        status__in=["pending", "accepted"],
    )
    note_topics = list(requests.values_list("topic", flat=True))
    note_filter = Q()
    for topic in note_topics:
        if topic:
            note_filter |= Q(tech__iexact=topic) | Q(mentor__profile__expertise__iexact=topic)
    matching_notes = MentorNote.objects.select_related("mentor", "mentor__profile").filter(note_filter) if note_filter else MentorNote.objects.none()
    mentor_messages = MentorMessage.objects.select_related("mentor", "mentor__profile").filter(student=request.user)[:10]

    return render(
        request,
        "student_dashboard.html",
        {
            "profile": profile,
            "full_name": f"{request.user.first_name} {request.user.last_name}".strip(),
            "mentors": mentors,
            "mentorship_requests": requests,
            "pending_count": requests.filter(status="pending").count(),
            "accepted_requests": requests.filter(status="accepted"),
            "matching_notes": matching_notes,
            "mentor_messages": mentor_messages,
            "accepted_count": requests.filter(status="accepted").count(),
            "notes_count": matching_notes.count(),
            "mentors_count": mentors.count(),
        },
    )


@ensure_csrf_cookie
def mentor_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("/")

    profile = request.user.profile
    if profile.role != "mentor":
        return redirect("/")

    pending_requests = MentorshipRequest.objects.select_related("student", "student__profile").filter(
        mentor=request.user,
        status="pending",
    )
    accepted_requests = MentorshipRequest.objects.select_related("student", "student__profile").filter(
        mentor=request.user,
        status="accepted",
    )
    notes = MentorNote.objects.filter(mentor=request.user)

    return render(
        request,
        "mentor_dashboard.html",
        {
            "profile": profile,
            "full_name": f"{request.user.first_name} {request.user.last_name}".strip(),
            "pending_requests": pending_requests,
            "accepted_requests": accepted_requests,
            "notes": notes,
            "pending_count": pending_requests.count(),
            "accepted_count": accepted_requests.count(),
            "notes_count": notes.count(),
        },
    )


def health_check(request):
    return JsonResponse({"status": "ok"})
