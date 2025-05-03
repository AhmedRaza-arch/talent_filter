# 12. Deployment Guide

## Preparing for Production

In this section, we'll explore how to deploy the Talent Filter application to a production environment. Deploying a Django application involves several steps to ensure it's secure, performant, and reliable.

## Production Settings

Before deploying, you need to configure production settings:

### Settings Module

Create a separate settings module for production:

```
Talent_Filter/
├── settings/
│   ├── __init__.py
│   ├── base.py      # Common settings
│   ├── dev.py       # Development settings
│   └── prod.py      # Production settings
```

#### Base Settings (base.py)

```python
# base.py
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'talent_filter_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Talent_Filter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'talent_filter_app.context_processors.notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'Talent_Filter.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/talent_filter.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'talent_filter_app': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

#### Production Settings (prod.py)

```python
# prod.py
from .base import *
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOSTS', 'talent-filter.example.com')]

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Security settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}

# Gemini API settings
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_API_URL = os.environ.get('GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent')

# Logging
LOGGING['handlers']['file']['filename'] = os.path.join(BASE_DIR, 'logs/talent_filter.log')
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['talent_filter_app']['level'] = 'INFO'
```

### Environment Variables

Create a `.env` file for environment variables:

```
# .env
DJANGO_SECRET_KEY=your-secret-key
ALLOWED_HOSTS=talent-filter.example.com
DB_NAME=talent_filter_db
DB_USER=talent_filter_user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@talent-filter.example.com
REDIS_URL=redis://127.0.0.1:6379/1
GEMINI_API_KEY=your-gemini-api-key
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent
```

## Database Setup

For production, you'll need to set up a MySQL database:

### MySQL Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

### Database Creation

```bash
# Log in to MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE talent_filter_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'talent_filter_user'@'localhost' IDENTIFIED BY 'your-db-password';
GRANT ALL PRIVILEGES ON talent_filter_db.* TO 'talent_filter_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Database Migration

```bash
# Apply migrations
python manage.py migrate --settings=Talent_Filter.settings.prod
```

## Web Server Setup

For production, you'll need a web server like Nginx and a WSGI server like Gunicorn:

### Gunicorn Installation

```bash
pip install gunicorn
```

### Gunicorn Configuration

Create a `gunicorn_config.py` file:

```python
# gunicorn_config.py
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5
```

### Nginx Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Nginx Configuration

Create a configuration file for your site:

```bash
# /etc/nginx/sites-available/talent-filter
server {
    listen 80;
    server_name talent-filter.example.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name talent-filter.example.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/talent-filter.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/talent-filter.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    
    # Static files
    location /static/ {
        alias /path/to/talent_filter/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
    
    # Media files
    location /media/ {
        alias /path/to/talent_filter/mediafiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }
    
    # Proxy requests to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
        proxy_read_timeout 30s;
    }
    
    # Error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /500.html;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/talent-filter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL Certificate

Secure your site with an SSL certificate using Let's Encrypt:

```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d talent-filter.example.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Process Management

Use Supervisor to manage the Gunicorn process:

```bash
# Install Supervisor
sudo apt update
sudo apt install supervisor
```

Create a configuration file:

```ini
# /etc/supervisor/conf.d/talent-filter.conf
[program:talent-filter]
command=/path/to/venv/bin/gunicorn -c /path/to/talent_filter/gunicorn_config.py Talent_Filter.wsgi:application
directory=/path/to/talent_filter
user=www-data
group=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/path/to/talent_filter/logs/gunicorn.log
```

Start the process:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status talent-filter
```

## Static and Media Files

Collect static files and create media directories:

```bash
# Collect static files
python manage.py collectstatic --settings=Talent_Filter.settings.prod

# Create media directory
mkdir -p /path/to/talent_filter/mediafiles
chmod 755 /path/to/talent_filter/mediafiles
```

## Redis Setup

Install and configure Redis for caching:

```bash
# Install Redis
sudo apt update
sudo apt install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Set supervised to systemd
# Set maxmemory 256mb
# Set maxmemory-policy allkeys-lru

# Restart Redis
sudo systemctl restart redis
```

## Backup Strategy

Implement a backup strategy for your database and media files:

### Database Backup

Create a backup script:

```bash
#!/bin/bash
# /path/to/talent_filter/scripts/backup_db.sh

# Set variables
BACKUP_DIR="/path/to/backups/database"
MYSQL_USER="talent_filter_user"
MYSQL_PASSWORD="your-db-password"
MYSQL_DATABASE="talent_filter_db"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/talent_filter_db_$DATE.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create backup
mysqldump -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE | gzip > $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "talent_filter_db_*.sql.gz" -type f -mtime +30 -delete
```

Make the script executable:

```bash
chmod +x /path/to/talent_filter/scripts/backup_db.sh
```

Schedule the backup with cron:

```bash
# Run backup daily at 2 AM
0 2 * * * /path/to/talent_filter/scripts/backup_db.sh
```

### Media Backup

Create a backup script:

```bash
#!/bin/bash
# /path/to/talent_filter/scripts/backup_media.sh

# Set variables
BACKUP_DIR="/path/to/backups/media"
MEDIA_DIR="/path/to/talent_filter/mediafiles"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/talent_filter_media_$DATE.tar.gz"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create backup
tar -czf $BACKUP_FILE -C $MEDIA_DIR .

# Remove backups older than 30 days
find $BACKUP_DIR -name "talent_filter_media_*.tar.gz" -type f -mtime +30 -delete
```

Make the script executable:

```bash
chmod +x /path/to/talent_filter/scripts/backup_media.sh
```

Schedule the backup with cron:

```bash
# Run backup daily at 3 AM
0 3 * * * /path/to/talent_filter/scripts/backup_media.sh
```

## Monitoring

Set up monitoring to ensure your application is running smoothly:

### Server Monitoring

Use a tool like Prometheus and Grafana for server monitoring:

```bash
# Install Prometheus Node Exporter
sudo apt update
sudo apt install prometheus-node-exporter

# Install Prometheus
sudo apt install prometheus

# Install Grafana
sudo apt install grafana
```

### Application Monitoring

Use Django's built-in logging to monitor application errors:

```python
# settings/prod.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/path/to/talent_filter/logs/django.log',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
        'talent_filter_app': {
            'handlers': ['file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}
```

## Deployment Checklist

Before going live, go through this checklist:

1. **Security**
   - [ ] Debug mode is off
   - [ ] Secret key is secure and not in version control
   - [ ] HTTPS is configured
   - [ ] Database credentials are secure
   - [ ] API keys are secure
   - [ ] Security middleware is enabled

2. **Performance**
   - [ ] Static files are collected and served by Nginx
   - [ ] Media files are properly configured
   - [ ] Database is optimized
   - [ ] Caching is configured

3. **Reliability**
   - [ ] Backups are configured
   - [ ] Monitoring is set up
   - [ ] Error logging is configured
   - [ ] Process management is in place

4. **Functionality**
   - [ ] All features work in production
   - [ ] Email sending works
   - [ ] File uploads work
   - [ ] API integrations work

## Deployment Script

Create a deployment script to automate the process:

```bash
#!/bin/bash
# /path/to/talent_filter/scripts/deploy.sh

# Set variables
APP_DIR="/path/to/talent_filter"
VENV_DIR="/path/to/venv"
BRANCH="main"

# Go to app directory
cd $APP_DIR

# Pull latest changes
git pull origin $BRANCH

# Activate virtual environment
source $VENV_DIR/bin/activate

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --settings=Talent_Filter.settings.prod

# Apply migrations
python manage.py migrate --settings=Talent_Filter.settings.prod

# Restart Gunicorn
sudo supervisorctl restart talent-filter

# Clear cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()" --settings=Talent_Filter.settings.prod

# Print success message
echo "Deployment completed successfully!"
```

Make the script executable:

```bash
chmod +x /path/to/talent_filter/scripts/deploy.sh
```

## Try It Yourself: Deployment Steps

Let's practice the deployment process:

1. Set up a virtual environment for the application
2. Configure production settings
3. Set up a database
4. Configure a web server
5. Implement a backup strategy

## Next Steps

In the next section, we'll explore learning exercises to reinforce your understanding of the Talent Filter application.
