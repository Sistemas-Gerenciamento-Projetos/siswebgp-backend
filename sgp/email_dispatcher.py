from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import send_mail
from django.conf import settings

activate_send_email = 0

def send_task_conclusion_email(project_name, id_task, task_link, manager_email):
    if activate_send_email:
        send_mail(
            'Tarefa concluída no projeto ' + project_name,
            'Olá, a tarefa de id #' + str(id_task) + ' foi concluída, acesse ' + task_link + ' para visualizar mais informações. \n\nAtenciosamente, Equipe SGP.',
            settings.EMAIL_HOST_USER,
            [manager_email],
            fail_silently=False,
        )

def send_task_update_email(project_name, id_task, task_link, manager_email):
    if activate_send_email:
        send_mail(
            'Tarefa alterada no projeto ' + project_name,
            'Olá, a tarefa de id #' + str(id_task) + ' foi alterada, acesse ' + task_link + ' para visualizar mais informações. \n\nAtenciosamente, Equipe SGP.',
            settings.EMAIL_HOST_USER,
            [manager_email],
            fail_silently=False,
        )