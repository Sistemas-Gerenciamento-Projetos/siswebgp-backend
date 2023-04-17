from django.db import models


class User(models.Model):
   nome = models.CharField(max_length=100)
   email = models.EmailField(max_length=254, unique=True)
   role = models.CharField(max_length=100)
   projects = models.ManyToManyField('Project', related_name='users', blank=True)

   def _str_(self):
       return f'{self.nome}, {self.role} - {self.email}'

class Project(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=100)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    deadline_date = models.DateTimeField(null=True, blank=True)
    
    def _str_(self):
         return f'{self.project_name} - {self.description}'
    
class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    deadline_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    epic = models.ForeignKey('Epic', on_delete=models.CASCADE, null=True, blank=True)
    
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
    user_invited = models.ForeignKey(User, on_delete=models.CASCADE)
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inviter')
    creation_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    accepted = models.BooleanField(default=False)
    
    def _str_(self):
         return f'{self.project} - {self.user} - {self.status}'