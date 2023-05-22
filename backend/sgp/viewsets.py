from sgp.serializers import *
from sgp.models import *
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    http_method_names = ['get']
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.order_by('name')

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [IsAdminUser]
        return super(self.__class__, self).get_permissions()

    def list(self, request):
        queryset = self.get_queryset()
        if queryset == JsonResponse({'message': 'Não há usuários cadastrados.'}):
            return JsonResponse({'message': 'Não foi possível recuperar usuários pois não há usuários cadastrados.'})
        else:
            serializer = UserSerializer(queryset, many=True)
            return JsonResponse(serializer.data, safe=False)

    def get_queryset(self):
        if not self.queryset.exists():
            return JsonResponse({'message': 'Não há usuários cadastrados.'})
        
        else:
            return self.queryset

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()

        if queryset == JsonResponse({'message': 'Não há usuários cadastrados.'}):
            return JsonResponse({'message': 'Não foi possível recuperar usuário pois não há usuários cadastrados.'})
        
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data)

    def get_object(self):
        pk = self.kwargs.get('pk')

        if pk == 'current':
            return self.request.user
        
        return super().get_object()

class ProjectViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [IsAdminUser]
        return super(self.__class__, self).get_permissions()

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def create_task(self, request, pk=None):
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project)
            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)
        
    def update(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid() and UserViewSet.get_object(self).id == project.manager.id:
            serializer.save()
            return JsonResponse(serializer.data)
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