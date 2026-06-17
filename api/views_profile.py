from django.http import JsonResponse

from .view_helpers import json_body, user_payload


ALLOWED_AVATAR_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def update_profile_info(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "Please sign in first."}, status=401)
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    data = json_body(request)
    if data is None:
        return JsonResponse({"ok": False, "error": "Invalid JSON."}, status=400)

    mobile = str(data.get("mobile", "")).strip()
    address = str(data.get("address", "")).strip()
    institute = str(data.get("institute", "")).strip()
    expertise = str(data.get("expertise", "")).strip()
    availability = str(data.get("availability", "")).strip()
    profile = request.user.profile
    availability_only = bool(availability) and not any([mobile, address, institute, expertise])

    if not availability_only and not mobile and not profile.mobile:
        return JsonResponse({"ok": False, "error": "Please enter your mobile number."}, status=400)
    if mobile and (len(mobile) < 7 or len(mobile) > 20):
        return JsonResponse({"ok": False, "error": "Enter a valid mobile number."}, status=400)
    if not availability_only and not address and not profile.address:
        return JsonResponse({"ok": False, "error": "Please enter your address."}, status=400)
    if not availability_only and not institute and not profile.institute:
        return JsonResponse({"ok": False, "error": "Please enter your institute or organization."}, status=400)
    if not availability_only and profile.role == "mentor" and not expertise and not profile.expertise:
        return JsonResponse({"ok": False, "error": "Please enter your expertise."}, status=400)

    if mobile:
        profile.mobile = mobile
    if address:
        profile.address = address
    if institute:
        profile.institute = institute
    if expertise:
        profile.expertise = expertise
    if availability:
        profile.availability = availability
    profile.save(update_fields=["mobile", "address", "institute", "expertise", "availability"])

    return JsonResponse({"ok": True, "user": user_payload(request.user)})


def update_profile_avatar(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "Please sign in first."}, status=401)
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    image = request.FILES.get("avatar")
    if not image:
        return JsonResponse({"ok": False, "error": "Choose an image to upload."}, status=400)
    if image.content_type not in ALLOWED_AVATAR_TYPES:
        return JsonResponse({"ok": False, "error": "Upload JPG, PNG, WebP, or GIF images only."}, status=400)
    if image.size > 3 * 1024 * 1024:
        return JsonResponse({"ok": False, "error": "Profile image must be 3 MB or smaller."}, status=400)

    profile = request.user.profile
    if profile.avatar_image:
        profile.avatar_image.delete(save=False)
    profile.avatar_image = image
    profile.save(update_fields=["avatar_image"])

    return JsonResponse({"ok": True, "user": user_payload(request.user)})
