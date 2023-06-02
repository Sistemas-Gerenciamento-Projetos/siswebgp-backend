$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if ($pythonPath -eq $null) {
    Write-Host "Python 3 não está instalado. Por favor, instale Python 3 e tente novamente."
    Exit 1
}

cd ..

Write-Host "Python 3 está instalado. Instalando virtual environment..."
python -m venv sgp-backend
Move-Item -Path .\backend -Destination .\sgp-backend
.\sgp-backend\Scripts\Activate.ps1

Write-Host "Instalando dependencias..."
pip install -r .\requirements.txt

Write-Host "Configurando base de dados..."
$files = Get-ChildItem -Path .\sgp-backend\backend\sgp\migrations -File

foreach ($file in $files) {
    if ($file.Name -ne "__init__.py") {
        Remove-Item -Path $file.FullName -Force
    }
}
python .\sgp-backend\backend\manage.py makemigrations
python .\sgp-backend\backend\manage.py migrate

Write-Host "Iniciando servidor local..."
python .\sgp-backend\backend\manage.py runserver