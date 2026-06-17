from pathlib import Path

from django.http import FileResponse, HttpResponseForbidden, JsonResponse

from .models import MentorNote
from .view_helpers import can_access_note, note_payload, require_role


def create_note(request):
    role_error = require_role(request, "mentor")
    if role_error:
        return role_error
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required."}, status=405)

    tech = str(request.POST.get("tech", "")).strip()
    title = str(request.POST.get("title", "")).strip()
    content = str(request.POST.get("content", "")).strip()
    document = request.FILES.get("document")

    if not tech:
        return JsonResponse({"ok": False, "error": "Please enter the tech/topic for this note."}, status=400)
    if not title:
        return JsonResponse({"ok": False, "error": "Please enter a note title."}, status=400)
    if not content and not document:
        return JsonResponse({"ok": False, "error": "Please add note content or upload a document."}, status=400)
    if document:
        allowed_extensions = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt"}
        extension = Path(document.name).suffix.lower()
        if extension not in allowed_extensions:
            return JsonResponse({"ok": False, "error": "Upload PDF, Word, PowerPoint, or text files only."}, status=400)
        if document.size > 10 * 1024 * 1024:
            return JsonResponse({"ok": False, "error": "Document must be 10 MB or smaller."}, status=400)

    note = MentorNote.objects.create(
        mentor=request.user,
        tech=tech,
        title=title,
        content=content,
        document=document,
    )
    return JsonResponse({"ok": True, "note": note_payload(note)}, status=201)


def download_note_document(request, note_id):
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "GET required."}, status=405)

    note = MentorNote.objects.select_related("mentor", "mentor__profile").filter(id=note_id).first()
    if not note or not note.document:
        return JsonResponse({"ok": False, "error": "Document not found."}, status=404)
    if not can_access_note(request.user, note):
        return HttpResponseForbidden("You do not have permission to access this document.")

    try:
        return FileResponse(
            note.document.open("rb"),
            as_attachment=True,
            filename=Path(note.document.name).name,
        )
    except FileNotFoundError:
        return JsonResponse({"ok": False, "error": "Document not found."}, status=404)
