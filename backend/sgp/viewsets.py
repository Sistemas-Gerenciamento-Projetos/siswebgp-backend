from sgp.serializers import *
from sgp.models import *
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import logging
logger = logging.getLogger('sgp_api')

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
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [IsAdminUser]
        return super(self.__class__, self).get_permissions()
    
    # Para fazer com que o body da requisição precise passar o id do gerente novamente,
    # é só deletar essa função.
    def create(self, request):
        data = request.data
        # Ou melhor, deletar essa linha.
        data['manager'] = request.user.id
        data['users'].append(request.user.id)
        serializer = ProjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def create_new_task(self, request, pk=None):
        project = Project.objects.get(pk=self.kwargs['pk'])

        if request.user.id != project.manager.id:
            return JsonResponse({'message': 'Você não tem permissão para criar tarefas neste projeto.'}, status=403)
        if request.data['user'] not in project.users.all():
            return JsonResponse({'message': 'O usuário informado não está associado a este projeto.'}, status=400)

        data = request.data
        data['project'] = self.kwargs['pk']

        logger.info(data)

        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)
        
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def projects_by_user(self, request):
        try:
            user = request.user
            projects = Project.objects.filter(users__id=user.id)
            serializer = ProjectSerializer(projects, many=True)
            return JsonResponse(serializer.data, safe=False)
        except user is None:
            return JsonResponse({'message': 'Usuário não encontrado.'}, status=404)
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        project = self.get_object()
        logger.info(f'Project name: {project.project_name}, project description: {project.description}')
        if request.user.id != project.manager.id:
            return JsonResponse({'message': 'Você não tem permissão para editar este projeto.'}, status=403)
        return super().partial_update(request, *args, **kwargs)
    
    def get_queryset(self):
        if not self.queryset.exists():
            return JsonResponse({'message': 'Não há projetos cadastrados.'})
        else:
            return self.queryset
    
class TaskViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.all()
        if queryset.exists():
            return self.queryset
        else:
            return JsonResponse({'message': 'Não há tarefas cadastradas.'})
        
    def list(self, request, project__pk=None):
        queryset = Task.objects.filter(project=project__pk)
        if not queryset.exists(): 
            return JsonResponse({'message': 'Não foi possível recuperar tarefas pois não há tarefas cadastradas.'})
        else:
            serializer = TaskSerializer(queryset, many=True)
            return JsonResponse(serializer.data, safe=False)

    def retrieve(self, request, project__pk=None, pk=None):
        queryset = Task.objects.filter(project=project__pk)
        if not queryset.exists():
            return JsonResponse({'message': 'Não foi possível recuperar tarefa pois não há tarefas cadastradas.'})
        task = get_object_or_404(queryset, pk=pk)
        serializer = TaskSerializer(task)
        return JsonResponse(serializer.data)
    
    def partial_update(self, request, project__pk=None, *args, **kwargs):
        kwargs['partial'] = True
        project = Project.objects.get(pk=project__pk)
        project_tasks = Task.objects.filter(project=project__pk)

        task = project_tasks.get(pk=kwargs['pk'])

        if request.data.get("status") is not None and (request.user.id != project.manager.id and request.user.id != task.user.id):
            return JsonResponse({'message': 'Você não tem permissão para alterar o status desta tarefa.'}, status=403)

        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return JsonResponse(serializer.data)

    # def get_object(self):
    #     lookup_field_value = self.kwargs[self.lookup_field]
    #     obj = Task.objects.get(lookup_field_value)
    #     self.check_object_permissions(self.request, obj)
    #     return obj