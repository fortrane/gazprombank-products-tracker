# 🏦 Gazprombank Reviews Analytics System (Frontend)

Система мониторинга и анализа отзывов клиентов для банковских продуктов в режиме реального времени.

## 📋 Описание проекта

Веб-приложение для отслеживания динамики клиентских настроений, анализа отзывов и выявления проблемных зон в банковских продуктах. Система предоставляет инструменты для визуализации данных, фильтрации по продуктам и временным периодам, а также автоматической категоризации отзывов по тональности.

## 💻 Системные требования

### Минимальные требования
- **ОС:** Ubuntu 22.04 LTS
- **Процессор:** 1 ядро
- **RAM:** 2 ГБ
- **Дисковое пространство:** 25 ГБ
- **Web-сервер:** Nginx
- **PHP:** 7.4
- **База данных:** MySQL 8.0+

### Сетевые требования
- Выделенный IP-адрес
- Доменное имя с настроенными DNS записями
- Открытые порты: 80, 443, 22

## 🚀 Установка

### Шаг 1: Подготовка домена

1. Направьте ваш домен на сервер через A-запись:
```
Type: A
Name: @
Value: [IP-адрес вашего сервера]
TTL: 3600
```

2. Создайте CNAME запись для поддомена www:
```
Type: CNAME
Name: www
Value: [ваш домен]
TTL: 3600
```

### Шаг 2: Базовая настройка сервера

1. Подключитесь к серверу по SSH и обновите систему:
```bash
sudo apt update
sudo apt upgrade -y
```

2. Установите необходимые пакеты:
```bash
sudo apt install nginx software-properties-common unzip nano curl ufw -y
```

### Шаг 3: Установка PHP 7.4

1. Добавьте репозиторий PHP:
```bash
sudo add-apt-repository ppa:ondrej/php -y
sudo apt update
```

2. Установите PHP и необходимые модули:
```bash
sudo apt install php7.4-fpm php7.4-common php7.4-mysql \
    php7.4-xml php7.4-xmlrpc php7.4-curl php7.4-gd \
    php7.4-imagick php7.4-cli php7.4-dev php7.4-imap \
    php7.4-mbstring php7.4-opcache php7.4-soap \
    php7.4-zip php7.4-intl -y
```

3. Запустите и включите PHP-FPM:
```bash
sudo systemctl enable php7.4-fpm
sudo systemctl start php7.4-fpm
```

### Шаг 4: Настройка MySQL

1. Установите MySQL Server:
```bash
sudo apt install mysql-server -y
```

2. Выполните безопасную настройку MySQL:
```bash
sudo mysql_secure_installation
```

При настройке ответьте на вопросы:
- Установить плагин валидации паролей? **Y** (выберите уровень 1 - MEDIUM)
- Установить пароль для root? **Y** (введите и запомните надежный пароль)
- Удалить анонимных пользователей? **Y**
- Запретить удаленный вход для root? **Y**
- Удалить тестовую базу данных? **Y**
- Перезагрузить таблицы привилегий? **Y**

3. Создайте пользователя для phpMyAdmin:
```bash
sudo mysql
```

В консоли MySQL выполните:
```sql
CREATE USER 'phpmyadmin'@'localhost' IDENTIFIED BY 'ВашСложныйПароль';
GRANT ALL PRIVILEGES ON *.* TO 'phpmyadmin'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
```

### Шаг 5: Установка phpMyAdmin

1. Загрузите phpMyAdmin 5.1.4:
```bash
cd /tmp
wget https://files.phpmyadmin.net/phpMyAdmin/5.1.4/phpMyAdmin-5.1.4-all-languages.tar.gz
tar xzf phpMyAdmin-5.1.4-all-languages.tar.gz
```

2. Переместите в системную директорию:
```bash
sudo mv phpMyAdmin-5.1.4-all-languages /usr/share/phpmyadmin
```

3. Создайте директорию для временных файлов:
```bash
sudo mkdir -p /var/lib/phpmyadmin/tmp
sudo chown -R www-data:www-data /var/lib/phpmyadmin/tmp
```

4. Настройте phpMyAdmin:
```bash
sudo cp /usr/share/phpmyadmin/config.sample.inc.php /usr/share/phpmyadmin/config.inc.php
sudo nano /usr/share/phpmyadmin/config.inc.php
```

Найдите и измените строку с `blowfish_secret`:
```php
$cfg['blowfish_secret'] = 'сгенерируйте32случайныхсимволаздесь';
```

В конец файла перед `?>` добавьте:
```php
$cfg['TempDir'] = '/var/lib/phpmyadmin/tmp';
```

### Шаг 6: Настройка веб-сервера

1. Создайте директорию для сайта:
```bash
sudo mkdir -p /var/www/ВАШ_ДОМЕН/public_html
sudo chown -R www-data:www-data /var/www/ВАШ_ДОМЕН
```

2. Скопируйте файлы проекта в директорию сайта:
```bash
# Загрузите файлы проекта в /var/www/ВАШ_ДОМЕН/public_html
```

3. Создайте символическую ссылку для phpMyAdmin:
```bash
sudo ln -s /usr/share/phpmyadmin /var/www/ВАШ_ДОМЕН/public_html/secret_admin_panel_2025
```

4. Создайте конфигурацию Nginx:
```bash
sudo nano /etc/nginx/sites-available/ВАШ_ДОМЕН
```

Добавьте следующую конфигурацию:
```nginx
server {
    listen 80;
    server_name ВАШ_ДОМЕН www.ВАШ_ДОМЕН;
    root /var/www/ВАШ_ДОМЕН/public_html;
    index index.php index.html index.htm;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location /secret_admin_panel_2025 {
        alias /usr/share/phpmyadmin/;
        index index.php;
        
        location ~ \.php$ {
            include snippets/fastcgi-php.conf;
            fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
            fastcgi_param SCRIPT_FILENAME $request_filename;
            include fastcgi_params;
        }
        
        location ~* ^/secret_admin_panel_2025/(.+\.(jpg|jpeg|gif|css|png|js|ico|html|xml|txt))$ {
            alias /usr/share/phpmyadmin/$1;
        }
    }

    location ~ /\.ht {
        deny all;
    }

    client_max_body_size 100M;
}
```

5. Активируйте сайт:
```bash
sudo ln -sf /etc/nginx/sites-available/ВАШ_ДОМЕН /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Шаг 7: Настройка PHP

1. Отредактируйте конфигурацию PHP:
```bash
sudo nano /etc/php/7.4/fpm/php.ini
```

2. Измените следующие параметры:
```ini
upload_max_filesize = 32M
post_max_size = 64M
max_execution_time = 100
```

3. Перезапустите PHP-FPM:
```bash
sudo systemctl restart php7.4-fpm
```

### Шаг 8: Настройка SSL

1. Установите Certbot:
```bash
sudo apt install certbot python3-certbot-nginx -y
```

2. Получите SSL сертификат:
```bash
sudo certbot --nginx -d ВАШ_ДОМЕН -d www.ВАШ_ДОМЕН
```

### Шаг 9: Настройка firewall

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw --force enable
```

### Шаг 10: Импорт базы данных

1. Войдите в phpMyAdmin через браузер:
```
https://ВАШ_ДОМЕН/secret_admin_panel_2025
```

2. Создайте новую базу данных `db_test`

3. Импортируйте файл из [папки database](https://github.com/fortrane/gazprombank-products-tracker/tree/main/database)

4. Создайте пользователя для приложения:
```sql
CREATE USER 'db_usr'@'localhost' IDENTIFIED BY 'ВашПароль';
GRANT ALL PRIVILEGES ON db_test.* TO 'db_usr'@'localhost';
FLUSH PRIVILEGES;
```

## ⚙️ Конфигурация

### Шаг 1: Настройка подключения к базе данных

Отредактируйте файл `/var/www/ВАШ_ДОМЕН/public_html/src/Custom/Medoo/connect.php`:

```php
$pdo = new PDO('mysql:dbname=db_test;host=localhost', 'db_usr', 'ВашПароль');
```

### Шаг 2: Настройка API

Отредактируйте файл `/var/www/ВАШ_ДОМЕН/public_html/src/Api/v1.php`:

```php
$apiUrl = "https://backend.example.com";  // URL вашего backend сервера
$secretKey = "ВАШ_СЕКРЕТНЫЙ_КЛЮЧ";       // API ключ, согласованный с backend
```

### Шаг 3: Установка прав доступа

```bash
sudo chown -R www-data:www-data /var/www/ВАШ_ДОМЕН/public_html
sudo chmod -R 755 /var/www/ВАШ_ДОМЕН/public_html
```

## 🔑 Доступ к системе

### Панель администратора
- **URL:** `https://ВАШ_ДОМЕН`
- **Логин:** `admin`
- **Пароль:** `admin`

### phpMyAdmin
- **URL:** `https://ВАШ_ДОМЕН/secret_admin_panel_2025`
- Используйте учетные данные, созданные при настройке MySQL
