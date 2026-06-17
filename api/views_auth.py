from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse

from .models import Profile
from .view_helpers import json_body, user_payload


def signup_user(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    data = json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "error": "Invalid JSON."}, status=400)

    first_name = str(data.get("firstName", "")).strip()
    last_name = str(data.get("lastName", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    role = str(data.get("role", "student")).strip()
    expertise = str(data.get("expertise", "")).strip()

    if not first_name or not last_name:
        return JsonResponse({"ok": False, "error": "Please enter your full name."}, status=400)
    if not email:
        return JsonResponse({"ok": False, "error": "Please enter your email address."}, status=400)
    if not username or len(username) < 3:
        return JsonResponse({"ok": False, "error": "Username must be at least 3 characters."}, status=400)
    if len(password) < 8:
        return JsonResponse({"ok": False, "error": "Password must be at least 8 characters."}, status=400)
    if role not in {"student", "mentor"}:
        return JsonResponse({"ok": False, "error": "Choose student or mentor."}, status=400)
    if role == "mentor" and not expertise:
        return JsonResponse({"ok": False, "error": "Please enter your primary expertise."}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"ok": False, "error": "That username is already taken."}, status=409)
    if User.objects.filter(email=email).exists():
        return JsonResponse({"ok": False, "error": "That email is already registered."}, status=409)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    Profile.objects.create(
        user=user,
        role=role,
        expertise=expertise,
        avatar=(first_name[:1] + last_name[:1]).upper(),
    )
    login(request, user)

    return JsonResponse({"ok": True, "user": user_payload(user)}, status=201)


def login_user(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    data = json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "error": "Invalid JSON."}, status=400)

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    user_record = User.objects.filter(email=email).first()
    if not user_record:
        return JsonResponse({"ok": False, "error": "No account found with that email."}, status=401)

    user = authenticate(request, username=user_record.username, password=password)
    if user is None:
        return JsonResponse({"ok": False, "error": "Incorrect password."}, status=401)

    login(request, user)
    return JsonResponse({"ok": True, "user": user_payload(user)})


def logout_user(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    logout(request)
    return JsonResponse({"ok": True})
