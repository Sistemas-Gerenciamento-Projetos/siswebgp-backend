from rest_framework import serializers
from .models import User, Project, Task, Epic, Invite

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'role', 'projects')
        read_only_fields = ('is_active', 'created', 'updated')
        
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'project', 'title', 'description', 'creation_date', 'start_date', 'deadline_date', 'status', 'user', 'epic')

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'manager', 'project_name', 'description', 'creation_date', 'start_date', 'deadline_date', 'users')

class EpicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Epic
        fields = ('id', 'title', 'description', 'creation_date', 'deadline_date', 'status', 'project')

class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = ('id', 'project', 'user_invited', 'inviter', 'creation_date', 'expiration_date', 'accepted')