from sgp.serializers import *
from sgp.models import *
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.db.models.query_utils import Q
import logging
logger = logging.getLogger('sgp_api')

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    http_method_names = ['get']
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.order_by('name')

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

        if data.get('users') is not None:
            data['users'].append(request.user.id)
        else:
            data['users'] = [request.user.id]

        start_date = datetime.fromisoformat(data['start_date'])
        deadline_date = datetime.fromisoformat(data['deadline_date'])

        if deadline_date < start_date:
            return JsonResponse({'message': 'A data de término não pode ser anterior à data de início.'}, status=400)

        serializer = ProjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def create_new_task(self, request, pk=None):
        project = Project.objects.get(pk=self.kwargs['pk'])
        data = request.data

        if request.user.id != project.manager.id:
            return JsonResponse({'message': 'Você não tem permissão para criar tarefas neste projeto.'}, status=403)
        if User.objects.get(pk=data['user']) not in project.users.all():
            return JsonResponse({'message': 'O usuário informado não está associado a este projeto.'}, status=400)

        start_date = datetime.fromisoformat(data['start_date'])
        deadline_date = datetime.fromisoformat(data['deadline_date'])

        if deadline_date < start_date:
            return JsonResponse({'message': 'A data de término não pode ser anterior à data de início.'}, status=400)

        data['project'] = self.kwargs['pk']
        project_tasks = Task.objects.filter(project=data['project'])
        if not project_tasks:
            data['number'] = 0
        else:
            greatest_number = project_tasks.order_by("-number")[0].number
            data['number'] = greatest_number + 1

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

            for project in serializer.data:
                project['manager_name'] = User.objects.get(pk=project['manager']).name
                project['num_completed_tasks'] = Task.objects.filter(project=project['id'], status='DONE').count()
                project['num_total_tasks'] = Task.objects.filter(project=project['id']).count()

            return JsonResponse(serializer.data, safe=False)
        except user is None:
            return JsonResponse({'message': 'Usuário não encontrado.'}, status=404)
        
    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticated])
    def project_users(self, request, pk=None):
        try:
            project = Project.objects.get(pk=self.kwargs['pk'])
            users = project.users.all()
            serializer = UserSerializer(users, many=True)
            for user in serializer.data:
                del user['projects']
                del user['email']
                del user['role']
            return JsonResponse(serializer.data, safe=False)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Projeto não encontrado.'}, status=404)

    @action(detail=True, methods=['GET'], permission_classes=[IsAuthenticated])
    def external_users(self, request, pk=None):
        try:
            project = Project.objects.get(pk=self.kwargs['pk'])

            if project is None:
                return JsonResponse({'message': 'Projeto não encontrado.'}, status=404)
            if request.user not in project.users.all():
                return JsonResponse({'message': 'Você não tem permissão para acessar este projeto.'}, status=403)
            
            users_not_in_project = User.objects.difference(project.users.all())
            serializer = UserSerializer(users_not_in_project, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Project.DoesNotExist:
            return JsonResponse({'message': f'Projeto com id {self.kwargs["pk"]} não encontrado.'}, status=404)
        
    
    @action(detail=True, methods=['GET', 'POST'], permission_classes=[IsAuthenticated])
    def include_users(self, request, pk=None):
        if request.method == 'GET':
            project = Project.objects.get(pk=self.kwargs['pk'])
            users_not_in_project = User.objects.difference(project.users.all())
            serializer = UserSerializer(users_not_in_project, many=True)
            return JsonResponse(serializer.data, safe=False)

        elif request.method == 'POST':
            project = Project.objects.get(pk=self.kwargs['pk'])
            data = request.data

            for user_id in data['users']:
                if User.objects.get(pk=user_id) not in project.users.all():
                    project.users.add(user_id)
                else:
                    return JsonResponse({'message': f'O usuário {User.objects.get(pk=user_id).email} já está associado a este projeto.'}, status=400)
                
            return JsonResponse({'message': 'Usuários adicionados com sucesso.'}, status=200)
        
        else:
            return JsonResponse({'message': 'Método não permitido.'}, status=405)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        project = self.get_object()
        if request.user.id != project.manager.id:
            return JsonResponse({'message': 'Você não tem permissão para editar este projeto.'}, status=403)
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if request.user.id != project.manager.id:
            return JsonResponse({'message': 'Você não tem permissão para deletar este projeto.'}, status=403)
        return super().destroy(request, *args, **kwargs)
    
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
            for task in serializer.data:
                task['user_name'] = User.objects.get(pk=task['user']).name
            return JsonResponse(serializer.data, safe=False)

    def retrieve(self, request, project__pk=None, pk=None):
        queryset = Task.objects.filter(project=project__pk)
        if not queryset.exists():
            return JsonResponse({'message': 'Não foi possível recuperar tarefa pois não há tarefas cadastradas.'})
        task = get_object_or_404(queryset, pk=pk)
        serializer = TaskSerializer(task)

        if serializer.data.get('user_name') is None:
            serializer_data = serializer.data
            serializer_data.update({'user_name': User.objects.get(pk=serializer.data['user']).name})
            return JsonResponse(serializer_data)
        else:
            return JsonResponse(serializer.data)
    
    def partial_update(self, request, project__pk=None, *args, **kwargs):
        kwargs['partial'] = True
        project = Project.objects.get(pk=project__pk)
        project_tasks = Task.objects.filter(project=project__pk)
        task = project_tasks.get(pk=kwargs['pk'])

        if request.data.get('project') is not None:
            return JsonResponse({'message': 'Você não pode alterar o projeto desta tarefa.'}, status=403)
        if request.data.get("status") is not None and (request.user.id != project.manager.id and request.user.id != task.user.id):
            return JsonResponse({'message': 'Você não tem permissão para alterar o status desta tarefa.'}, status=403)

        serializer = self.get_serializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return JsonResponse(serializer.data)
    
    def destroy(self, request, project__pk=None, *args, **kwargs):
        project = Project.objects.get(pk=project__pk)
        project_tasks = Task.objects.filter(project=project__pk)

        task = project_tasks.get(pk=kwargs['pk'])
        if request.user.id != project.manager.id:
            return JsonResponse({'message': 'Você não tem permissão para deletar esta tarefa.'}, status=403)

        self.perform_destroy(task)
        return JsonResponse({'message': 'Tarefa deletada com sucesso.'}, status=200)

class InviteViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post']
    serializer_class = InviteSerializer
    permission_classes = [IsAuthenticated]

class EpicViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = EpicSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, project__pk=None):
        project__pk = request.GET.get('project_id', None)
        if project__pk is None:
            return JsonResponse({'message': 'Campo project_id inválido'}, status=400)

        queryset = Epic.objects.filter(project=project__pk)

        if not queryset.exists():
            return JsonResponse([], status=200, safe=False)
        
        serializer = EpicSerializer(queryset, many=True)

        for epic in serializer.data:
                epic['user_name'] = User.objects.get(pk=epic['user']).name

        return JsonResponse(serializer.data, safe=False)

    def create(self, request):
        data = request.data

        project_id = request.data.get('project_id')
        project_epics = Epic.objects.filter(project=project_id)
        if not project_epics:
            data['number'] = 0
        else:
            greatest_number = project_epics.order_by("-number")[0].number
            data['number'] = greatest_number + 1

        serializer = EpicSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)

    def partial_update(self, request, project__pk=None, *args, **kwargs):
        kwargs['partial'] = True
        project = Project.objects.get(pk=project__pk)
        project_epics = Epic.objects.filter(project=project__pk)
        epic = project_epics.get(pk=kwargs['pk'])

        serializer = self.get_serializer(epic, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return JsonResponse(serializer.data)
