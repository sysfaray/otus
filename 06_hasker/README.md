# Hasker HomeWork

Django, система вопросов и ответов

### Deploy 

Для работы нам понадобиться установленный Centos 7, git и make

Клонируем репозеторий 
    
    cd /opt/
    git clone git@github.com:sysfaray/otus.git

Создаем директорию hasker и копируем файлы урока в эту директорию
    
    mkdir hasker
    cp -r otus/06_hasker/* hasker
    cd hasker

Добавляем права на запись для директории media

    chmod -R 777 code/hasker/media/
    
Выпонялем установку Docker, Docker-Compose
    
    make prod
    
Выполняем создание суперпользователя

    docker-compose exec django python manage.py createsuperuser

## API

Документация к API

    http://ip/api/docs/

Swagger-схема находится в файле swagger.yaml
