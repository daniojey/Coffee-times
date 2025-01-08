from django.contrib import admin

from users.models import User
from unfold.admin import ModelAdmin

@admin.register(User)
class CustomUserClass(ModelAdmin):
    pass