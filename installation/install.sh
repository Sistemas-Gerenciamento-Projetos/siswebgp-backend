#!/bin/bash

# Checa se o Python3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não está instalado. Por favor instale o Python 3 e tente novamente."
    exit 1
fi

# Cria o venv e ativa
python3 -m venv myenv
source myenv/bin/activate

# Instala as dependências
pip install -r requirements.txt

# Executa as migrações e coleta os arquivos estáticos
python manage.py migrate
python manage.py collectstatic

# Inicia o servidor local
python manage.py runserver