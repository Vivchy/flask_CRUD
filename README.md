<h1 align="center">Пример CRUD на flask с разворотом на сервере nginx</h1>

![GitHub repo file count](https://img.shields.io/github/directory-file-count/Vivchy/flask_CRUD)
![GitHub repo size](https://img.shields.io/github/repo-size/vivchy/flask_CRUD)
![GitHub top language](https://img.shields.io/github/languages/top/Vivchy/flask_crud)

## Установка зависимостей

> sudo apt update

> sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools

### venv

>sudo apt install python3-venv

или

> pip install virtualenv

### В папке с проектом создать *venv*

> python3 -m venv venv 

или

> virtualenv venv

### запусть venv

> source venv/bin/activate

### установить зависимости
> pip install -r req.txt
> pip install wheel
> pip install uwsgi
> 
<h3 align="center">Инициализация бд </h3>

>python

<pre>
    from main import db

    db.create_all()
</pre>

### доступ к портам

> sudo ufw allow 5000

### Тестовый запуск приложения 

> uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app

****

***

### Файл конфигурации uwsgi в `wsgi.ini`

### Создание служебного файла systemd
> sudo nano /etc/systemd/system/flask_crud.service

<pre>
[Unit]
Description=uWSGI instance to serve flask - nginx
After=network.target

[Service]
User=vivchy
Group=www-data
WorkingDirectory=/home/user/flask_CRUD
Environment="PATH=/home/user/flask_CRUD/venv/bin"
ExecStart=/home/user/flask_CRUD/venv/bin/uwsgi --ini wsgi.ini

[Install]
WantedBy=multi-user.target
</pre>

### Запуск 
> sudo systemctl start myproject
> 
> sudo systemctl enable myproject
> 
> sudo systemctl status myproject

***

## Настройка NGINX

### Создание файла конфигурации

> sudo nano /etc/nginx/sites-available/flask_crud

<pre>
server {
    listen 80;
    server_name your_domain www.your_domain;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/home/user/flask_crud/flasktonginx.sock;
    }
}
</pre>

>sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
> 
> sudo nginx -t
> 
> sudo systemctl restart nginx
> 
> sudo ufw delete allow 5000
> 
>sudo ufw allow 'Nginx Full'

Сайт будет доступен на привязанном url 

[источник](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04-ru)


    