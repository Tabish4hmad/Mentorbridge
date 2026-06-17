from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("mentor", "Mentor"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    expertise = models.CharField(max_length=255, blank=True)
    avatar = models.CharField(max_length=8, blank=True)
    avatar_image = models.FileField(upload_to="profile_images/", blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    institute = models.CharField(max_length=255, blank=True)
    availability = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class MentorshipRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
        ("cancelled", "Cancelled"),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_mentorship_requests")
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_mentorship_requests")
    topic = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "mentor"],
                condition=models.Q(status="pending"),
                name="unique_pending_request_per_student_mentor",
            )
        ]

    def __str__(self):
        return f"{self.student.username} -> {self.mentor.username} ({self.status})"


class MentorNote(models.Model):
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mentor_notes")
    tech = models.CharField(max_length=120)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    document = models.FileField(upload_to="mentor_notes/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.tech})"


class MentorMessage(models.Model):
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_student_messages")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_mentor_messages")
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.mentor.username} -> {self.student.username}"


class ChatThread(models.Model):
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mentor_chat_threads")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_chat_threads")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(fields=["mentor", "student"], name="unique_chat_thread_per_pair")
        ]

    def __str__(self):
        return f"{self.mentor.username} <-> {self.student.username}"


class ChatMessage(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_chat_messages")
    body = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender.username}: {self.body[:32]}"
