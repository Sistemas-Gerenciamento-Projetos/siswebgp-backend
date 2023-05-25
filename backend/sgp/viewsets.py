from sgp.serializers import *
from sgp.models import *
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    http_method_names = ['get']
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.order_by('name')

    def get_queryset(self):
        if not self.queryset.exists():
            return JsonResponse({'message': 'Não há usuários cadastrados.'})

        else:
            return self.queryset

    def get_object(self):
        lookup_field_value = self.kwargs[self.lookup_field]
        obj = User.objects.get(lookup_field_value)
        self.check_object_permissions(self.request, obj)
        return obj


class ProjectViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def create_task(self, request, pk=None):
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project)
            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)

    def get_queryset(self):
        if not self.queryset.exists():
            return JsonResponse({'message': 'Não há projetos cadastrados.'})
        else:
            return self.queryset

    def get_object(self):
        lookup_field_value = self.kwargs[self.lookup_field]
        obj = Project.objects.get(lookup_field_value)
        self.check_object_permissions(self.request, obj)
        return obj


class TaskViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.all()
        if queryset.exists():
            return self.queryset
        else:
            return JsonResponse({'message': 'Não há tarefas cadastradas.'})

    def get_object(self):
        lookup_field_value = self.kwargs[self.lookup_field]
        obj = Task.objects.get(lookup_field_value)
        self.check_object_permissions(self.request, obj)
        return obj
