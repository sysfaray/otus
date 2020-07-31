# Приложение 

Приложение подсчета стоимости работ в автосервисе.

### Deploy 

Для работы нам понадобиться установленный Centos 7, git и make

Клонируем репозеторий 
    
    cd /opt/
    git clone git@github.com:sysfaray/otus.git

Создаем директорию hasker и копируем файлы урока в эту директорию
    
    mkdir serv
    cp -r otus/serv/* serv
    cd serv

Добавляем права на запись для директории media

    chmod -R 777 code/static/media/
    
Выпонялем установку Docker, Docker-Compose
    
    make prod
    
Выполняем создание суперпользователя

    docker-compose exec django python manage.py createsuperuser

Выполняем импортирование данных

    Переходим по админку по адерсу http://xxxxxx/admin
    Заходим во вкладку Car и нажимаем импорт, добавляем файл car.xlsx из папки files в проекте.
    Жмем импорт и ждем заверешения выполнения.
    
    Заходим во вкладку Запчасти оригинал и импортируем таким же образом файл price2.xlsx
    
    Заходим во вкладку Вид работ и импортируем таким же образом файл price2.xlsx
    
## API ##

    В разработке