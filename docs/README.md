# Instalando dependências do sistema operacional

```
sudo apt-get update
sudo apt-get install git-core curl --yes
```

```
sudo apt-fast -y install python-dev gettext build-essential libssl-dev zlib1g-dev libpq-dev
```

## Instalando `apt-fast` (acelerador de downloads para `apt-get`)

```bash
/bin/bash -c "$(curl -sL https://git.io/vokNn)"
```

Se o download do arquivo acima não funcionar, execute o comando abaixo

```bash
#!/bin/bash
sudo apt-get install -y aria2 git
if ! [[ -f /usr/bin/apt-fast ]]; then
  git clone https://github.com/ilikenwf/apt-fast /tmp/apt-fast
  sudo cp /tmp/apt-fast/apt-fast /usr/bin
  sudo chmod +x /usr/bin/apt-fast
  sudo cp /tmp/apt-fast/apt-fast.conf /etc
fi
```

## Instalando o `pip` (gerenciador de pacotes python)

```bash
cd /tmp; wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py; sudo -H python2 get-pip.py -U; cd -
```

## Instalando `virtualenv` e `virtualenvwrapper`

```bash
sudo -H pip install virtualenv virtualenvwrapper
```


### Configurando VirtualEnvWrapper

```bash
echo -e "export WORKON_HOME=$HOME/.virtualenvs\nsource /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc

source ~/.bashrc
```

# Configurando o pip para utilizar cache

```bash
mkdir -p ~/.config/pip/

echo -e "[global]\nindex-url = http://root:test@pypi.defensoria.to.gov.br:4040/root/pypi/+simple/\ntrusted-host = pypi.defensoria.to.gov.br\nextra-index-url = https://pypi.python.org/simple" | tee ~/.config/pip/pip.conf
```

# Instalando MongoDB no Debian 8
https://docs.mongodb.com/manual/tutorial/install-mongodb-on-debian/

```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6

echo "deb http://repo.mongodb.org/apt/debian jessie/mongodb-org/3.4 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list

sudo apt-get update

sudo apt-get install -y mongodb-org
```

# Clonando projeto
```bash
cd $HOME

git clone https://github.com/lmoabreu/ProcAPI procapi
```

## Configurando arquivo .env
```ini
#Sample .env

DEBUG=off
SECRET_KEY=*@#$%$#@#$@#$@#&%
ALLOWED_HOSTS=127.0.0.1, localhost

RAVEN_DSN=https://<key>:<secret>@sentry.io/<project>

MONGO_DBNAME=db_name
MONGO_HOSTNAME=localhost
MONGO_PORT=27017
MONGO_USER=user
MONGO_PASSWORD=password

EPROC_DEFAULT_USER=UserEprocWSDL
EPROC_DEFAULT_PASS=PassUserEprocWSDL

EPROC_WSDL_PROCESSOS=http://127.0.0.1/wsdl/processos
EPROC_WSDL_SERVICOS=http://127.0.0.1/wsdl/servicos
EPROC_WSDL_TABELAS=http://127.0.0.1/wsdl/servicos

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

```

## Criando virtualenv

```bash
mkvirtualenv procapi -p python2
```


## Instalando requirements

```bash
pip install -r requirements/production.txt 
```

## Criando arquivos estáticos

```bash
./manage.py collectstatic
```

# Instalando UWSGI

[Tutorial: Como servir aplicativos do Django com uWSGI e Nginx no Debian 8](https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-uwsgi-and-nginx-on-debian-8)

```bash
sudo -H pip install uwsgi
uwsgi --http :8000 --home diretorio_do_virtualenv --chdir diretorio_do_projeto -w config.wsgi
```

```bash
sudo mkdir -p /etc/uwsgi/sites
cd /etc/uwsgi/sites
sudo nano procapi.ini
```

# Configurações UWSGI

```ini
[uwsgi]
project = procapi
uid = desenvolvimento
gid = www-data

base = /home/%(uid)

chdir = %(base)/%(project)
home = %(base)/.virtualenvs/%(project)
module = config.wsgi:application

master = true
processes = 4

# Finish off the configuration with the following lines
socket = /run/uwsgi/%(project).sock
chown-socket = %(uid):%(gid)
chmod-socket = 664
vacuum = true
```

# Configurando serviço UWSGI

## Crie o arquivo uwsgi.service

```
sudo nano /etc/systemd/system/uwsgi.service
```

## Conteúdo do arquivo uwsgi.service

```ini
[Unit]
Description=uWSGI Emperor service

[Service]
ExecStartPre=/bin/bash -c 'mkdir -p /run/uwsgi; chown desenvolvimento:www-data /run/uwsgi'
ExecStart=/usr/local/bin/uwsgi --emperor /etc/uwsgi/sites
Restart=always
KillSignal=SIGQUIT
Type=notify
NotifyAccess=all

[Install]
WantedBy=multi-user.target
```

## Habilite e inicialize o serviço do UWSGI

```
sudo systemctl enable uwsgi
sudo systemctl restart uwsgi
```

# Instalando e Configurando NGINX

```bash
sudo apt-get install nginx
```

## Crie o arquivo do site NGINX

```bash
sudo nano /etc/nginx/sites-available/procapi
```

## Conteúdo do arquivo do site

```nginx
server {
    listen 80;
    server_name procapi.domain.com;

    root /home/desenvolvimento/procapi;

    error_log /home/desenvolvimento/procapi/log/nginx/error.log;
    access_log /home/desenvolvimento/procapi/log/nginx/access.log;

    location = /favicon.ico { access_log off; log_not_found off; }

    location / {
        include         uwsgi_params;
        uwsgi_pass      unix:/run/uwsgi/procapi.sock;
    }

    location /media {
        alias /home/desenvolvimento/procapi/media_producao;
    }

    location /static {
        alias /home/desenvolvimento/procapi/static_producao;
    }

}
```

## Crie o link simbólico no diretório de sites ativos

```bash
sudo ln -s /etc/nginx/sites-available/procapi /etc/nginx/sites-enabled
```

## Valide a configuração do NGINX

```bash
sudo nginx -t
```

## Habilite e inicialize o serviço do NGINX

```bash
sudo systemctl enable nginx
sudo systemctl restart nginx
```