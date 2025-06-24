from django.contrib import admin

from users.models import User
from unfold.admin import ModelAdmin, TabularInline
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group

class MyTabularInline(TabularInline):
    model = User
    tab = True

admin.site.unregister(Group)

@admin.register(User)
class CustomUserClass(ModelAdmin):
    pass

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass