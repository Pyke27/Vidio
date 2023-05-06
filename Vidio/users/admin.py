from django.contrib import admin
from .models import Profile, AudioFile, User, PossibleAdmin

admin.site.register(Profile)
admin.site.register(AudioFile)

admin.site.register(PossibleAdmin)
