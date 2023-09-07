from django.test import TestCase
from django.core import serializers
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, Project, Task

BASE_URL = 'http://127.0.0.1:8000/api/'

class RegistrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
    def test_registration(self):
        body = {
            'email': 'generico@generico.com',
            'password': 'generico',
            'username': 'generico',
            'name': 'Generico'
        }
        
        url = f'{BASE_URL}auth/register/'
        response = self.client.post(url, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user = User.objects.get(email='generico@generico.com')
        self.assertIsNotNone(new_user)

class CreateProjectTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        User.objects.create_user(name='Bruno Correia', email='brunoteste@pymail.com', password='brunoteste')
        self.user = User.objects.get(email='brunoteste@pymail.com')
        self.client.force_authenticate(user=self.user)
    def test_create_project(self):
        body_create_project_request = {
            'manager': f'{self.user.id}',
            'project_name': 'Projeto Teste',
            'description': 'Descrição do projeto teste',
            'deadline_date': '2021-12-31',
            'users': [
                f'{self.user.id}'
            ]
        }
        url = f'{BASE_URL}projects/'
        response = self.client.post(url, body_create_project_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class GetProjectsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        User.objects.create_user(name='Bruno Correia', email='brunoteste@pymail.com', password='brunoteste')
        self.user = User.objects.get(email='brunoteste@pymail.com')
        self.client.force_authenticate(user=self.user)

    def test_get_projects(self):
        Project.objects.create(manager=self.user, project_name='Projeto Teste', description='Descrição do projeto teste', deadline_date='2021-12-31')
        url = f'{BASE_URL}projects/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class CreateTaskTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(name='Bruno Correia', email='brunoteste@pymail.com', password='brunoteste')
        self.project = Project.objects.create(manager=self.user, project_name='Projeto Teste', description='Descrição do projeto teste', deadline_date='2021-12-31')
        self.user.projects.add(self.project)
        self.client.force_authenticate(user=self.user)

    def test_create_task(self):
        body_create_task_request = {
            'project': f'{self.project.id}',
            'title': 'Tarefa Teste',
            'description': 'Descrição da tarefa teste',
            'deadline_date': '2021-12-31',
            'status': 'TODO',
            'user': f'{self.user.id}'
        }

        url = f'{BASE_URL}projects/{self.project.id}/tasks/'
        response = self.client.post(url, body_create_task_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)