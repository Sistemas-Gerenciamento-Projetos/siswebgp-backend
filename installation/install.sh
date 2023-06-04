#!/bin/bash

pythonPath=$(command -v python3)
if [[ -z $pythonPath ]]; then
    echo "Python 3 não está instalado. Por favor, instale Python 3 e tente novamente."
    exit 1
fi

cd ..

echo "Python 3 está instalado. Instalando virtual environment..."
sudo apt install python3.10-venv
python3 -m venv sgp-backend
mv backend sgp-backend
source sgp-backend/bin/activate

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Configurando base de dados..."
files=$(find sgp-backend/backend/sgp/migrations -type f)

for file in $files; do
    if [[ $(basename "$file") != "__init__.py" ]]; then
        rm -f "$file"
    fi
done

python3 sgp-backend/backend/manage.py makemigrations
python3 sgp-backend/backend/manage.py migrate

echo "Iniciando servidor local..."
python3 sgp-backend/backend/manage.py runserver