from django.contrib import admin

from .models import MentorNote, MentorshipRequest, Profile


admin.site.register(Profile)
admin.site.register(MentorshipRequest)
admin.site.register(MentorNote)
