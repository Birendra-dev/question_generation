# Register your models here
from django.contrib import admin
from .models import Profile,MCQ

admin.site.register(MCQ)
admin.site.register(Profile)