from django.http import JsonResponse

from .models import ChatMessage
from .view_helpers import (
    chat_message_payload,
    chat_thread_payload,
    ensure_chat_threads,
    get_accessible_thread,
    json_body,
)


def chat_threads(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "Please sign in first."}, status=401)
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "GET required."}, status=405)
    if request.user.profile.role not in {"mentor", "student"}:
        return JsonResponse({"ok": False, "error": "Only mentors and students can use inbox."}, status=403)

    threads = ensure_chat_threads(request.user)
    return JsonResponse({"ok": True, "threads": [chat_thread_payload(thread, request.user) for thread in threads]})


def chat_thread_messages(request, thread_id):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "Please sign in first."}, status=401)

    thread = get_accessible_thread(request.user, thread_id)
    if not thread:
        return JsonResponse({"ok": False, "error": "Conversation not found."}, status=404)

    if request.method == "GET":
        messages = thread.messages.select_related("sender").all()
        after_id = request.GET.get("after")
        if after_id:
            messages = messages.filter(id__gt=after_id)
        return JsonResponse(
            {
                "ok": True,
                "thread": chat_thread_payload(thread, request.user),
                "messages": [chat_message_payload(message, request.user) for message in messages],
            }
        )

    if request.method == "POST":
        data = json_body(request)
        if data is None:
            return JsonResponse({"ok": False, "error": "Invalid JSON."}, status=400)

        body = str(data.get("body", "")).strip()
        if not body:
            return JsonResponse({"ok": False, "error": "Write a message first."}, status=400)
        if len(body) > 1000:
            return JsonResponse({"ok": False, "error": "Message must be 1000 characters or fewer."}, status=400)

        message = ChatMessage.objects.create(thread=thread, sender=request.user, body=body)
        thread.save(update_fields=["updated_at"])
        return JsonResponse({"ok": True, "message": chat_message_payload(message, request.user)}, status=201)

    return JsonResponse({"ok": False, "error": "GET or POST required."}, status=405)

