# siswebgp-backend

## Como instalar?

- Ter python3 instalado, segue link de tutorial de instalação [Linux](https://python-guide-pt-br.readthedocs.io/pt_BR/latest/starting/install3/linux.html), [Windows](https://python.org.br/instalacao-windows/), [MacOS](https://docs.python-guide.org/starting/install3/osx/);

- Clonar este repositório;

- Dentro da pasta do repositório clonado, rodar o seguinte comando
no Linux/MacOS:
```
python3 -m venv env
```

no Windows:
```
pip install virtualenv
```
```
virtualenv env
```

- Para ativar o virtualenv no MacOS/Linux:

```
source env/bin/activate
```

- Para ativar o virtualenv no Windows:

```
env/Scripts/activate.bat
```

- Com o virtualenv ativado basta rodar:

```
pip install Flask
```

- Para rodar a aplicação execute:

```
flask run
