import json

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .models import ChatMessage, ChatThread, MentorMessage, MentorshipRequest, Profile


class MentorMessageTests(TestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(
            username="mentor",
            email="mentor@example.com",
            password="password123",
            first_name="Mina",
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="password123",
            first_name="Sam",
        )
        Profile.objects.create(user=self.mentor, role="mentor", avatar="M", expertise="Django")
        Profile.objects.create(user=self.student, role="student", avatar="S")

    def test_connected_mentor_can_send_student_message(self):
        MentorshipRequest.objects.create(
            mentor=self.mentor,
            student=self.student,
            topic="Django",
            status="accepted",
        )
        self.client.login(username="mentor", password="password123")

        response = self.client.post(
            "/api/messages/",
            data=json.dumps({"studentId": self.student.id, "message": "Please review chapter 2."}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(MentorMessage.objects.filter(student=self.student, mentor=self.mentor).exists())

    def test_mentor_cannot_message_unconnected_student(self):
        self.client.login(username="mentor", password="password123")

        response = self.client.post(
            "/api/messages/",
            data=json.dumps({"studentId": self.student.id, "message": "Hello."}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(MentorMessage.objects.exists())

    def test_user_can_upload_profile_avatar(self):
        self.client.login(username="student", password="password123")
        image = SimpleUploadedFile(
            "avatar.png",
            b"\x89PNG\r\n\x1a\nprofile-image",
            content_type="image/png",
        )

        response = self.client.post("/api/profile/avatar/", {"avatar": image})

        self.assertEqual(response.status_code, 200)
        self.student.profile.refresh_from_db()
        self.assertTrue(self.student.profile.avatar_image.name.startswith("profile_images/"))
        self.assertTrue(response.json()["user"]["avatarUrl"])


class InboxChatTests(TestCase):
    def setUp(self):
        self.mentor = User.objects.create_user(
            username="chatmentor",
            email="chatmentor@example.com",
            password="password123",
            first_name="Maya",
        )
        self.student = User.objects.create_user(
            username="chatstudent",
            email="chatstudent@example.com",
            password="password123",
            first_name="Sid",
        )
        self.other_student = User.objects.create_user(
            username="outsider",
            email="outsider@example.com",
            password="password123",
            first_name="Out",
        )
        Profile.objects.create(user=self.mentor, role="mentor", avatar="M", expertise="Python")
        Profile.objects.create(user=self.student, role="student", avatar="S")
        Profile.objects.create(user=self.other_student, role="student", avatar="O")
        MentorshipRequest.objects.create(
            mentor=self.mentor,
            student=self.student,
            topic="Python",
            status="accepted",
        )

    def test_inbox_creates_thread_for_accepted_connection(self):
        self.client.login(username="chatstudent", password="password123")

        response = self.client.get("/api/inbox/threads/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["threads"][0]["partnerName"], "Maya")
        self.assertTrue(ChatThread.objects.filter(mentor=self.mentor, student=self.student).exists())

    def test_both_sides_can_send_messages_in_thread(self):
        thread = ChatThread.objects.create(mentor=self.mentor, student=self.student)
        self.client.login(username="chatmentor", password="password123")

        mentor_response = self.client.post(
            f"/api/inbox/threads/{thread.id}/messages/",
            data=json.dumps({"body": "Please share your progress."}),
            content_type="application/json",
        )
        self.client.logout()
        self.client.login(username="chatstudent", password="password123")
        student_response = self.client.post(
            f"/api/inbox/threads/{thread.id}/messages/",
            data=json.dumps({"body": "I completed the first task."}),
            content_type="application/json",
        )

        self.assertEqual(mentor_response.status_code, 201)
        self.assertEqual(student_response.status_code, 201)
        self.assertEqual(ChatMessage.objects.filter(thread=thread).count(), 2)

    def test_unrelated_user_cannot_open_thread(self):
        thread = ChatThread.objects.create(mentor=self.mentor, student=self.student)
        self.client.login(username="outsider", password="password123")

        response = self.client.get(f"/api/inbox/threads/{thread.id}/messages/")

        self.assertEqual(response.status_code, 404)
