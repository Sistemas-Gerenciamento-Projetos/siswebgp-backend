from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Usuários devem ter um endereço de e-mail')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
   id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
   name = models.CharField(max_length=100)
   email = models.EmailField(max_length=254, unique=True)
   password = models.CharField(max_length=128)
   role = models.CharField(max_length=100)
   projects = models.ManyToManyField('Project', related_name='users', blank=True)
   is_staff = models.BooleanField(default=False)
   
   objects = CustomUserManager()

   USERNAME_FIELD = 'email'
   REQUIRED_FIELDS = ['name']

   def get_projects(self):
       return '\n'.join([project.project_name for project in self.projects.all()])

   def _str_(self):
       return f'{self.name}, {self.role} - {self.email}'

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_projects')
    project_name = models.CharField(max_length=100)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=False, blank=False, default=timezone.now)
    deadline_date = models.DateTimeField(null=False, blank=False)
    
    def _str_(self):
         return f'{self.project_name} - {self.description}'
    
class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=False, blank=False)
    deadline_date = models.DateTimeField(null=False)
    status = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    epic = models.ForeignKey('Epic', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    
    def _str_(self):
         return f'{self.title}'
    
class Epic(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    deadline_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    def _str_(self):
         return f'{self.title}'

class Invite(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # user_invited = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='invites_received')
    invited_user = models.EmailField(max_length=254, null=False)
    inviter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='invites')
    creation_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    accepted = models.BooleanField(default=False)
    
    def _str_(self):
         return f'{self.project} - {self.user} - {self.status}'