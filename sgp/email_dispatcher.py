from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import send_mail

def send_task_conclusion_email(project_name, id_task, task_link, manager_email):
    send_mail(
        'Tarefa concluída no projeto ' + project_name,
        'Olá, a tarefa de id #' + str(id_task) + ' foi concluída, acesse ' + task_link + ' para visualizar mais informações. \n\nAtenciosamente, Equipe SGP.',
        settings.EMAIL_HOST_USER,
        [manager_email],
        fail_silently=False,
    )


# + id_task + ' foi concluída, acesse para visualizar mais informações. /n/nAtenciosamente, Equipe SGP.'

# Esboço email
# Titulo: Tarefa concluida no projeto (nome do projeto)
# Mensagem: Olá, a tarefa de id (numero do id), foi concluida,
#           acesse o link (colocar o link) para visualizar mais informações
#           Atenciosamente, Equipe SGP.