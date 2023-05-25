from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import User, Project, Task, Epic, Invite

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'role', 'get_projects')

User = get_user_model()

admin.site.register(User, UserAdmin)