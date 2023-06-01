# discogskiii-django
a web app and order book for vinyl records available for sale on discogs!

---
### Reference:

---
#### Django
Install Django:
```pip3 install Django```

Create Project:
```django-admin startproject PROJECT_NAME```

Run Server:
```python manage.py runserver```

Create App:
```python manage.py startapp APP_NAME```

Add APP_NAME to discogskiii/settings.py INSTALLED_APPS list

Add urls.py file to discogskiii/APP_NAME

Add APP_NAME to discogskiii/urls.py

Add discogskiii/firstapp/templates/firstapp/index.html for HTML

---
#### Django HTML Templating
Insert a variable:
{{ VARIABLE }}

Logical:
{% if CONDITION %}
    Yes
{% else %}
    No
{% endif %}

Add CSS to an HTML file
{% load static %}
Then link with templating language
<link href="{% static 'APP_NAME/styles.css' %}" rel="stylesheet">
__sometimes you need to restart the server to load static files__

---
#### Virtual Environments
Create Python3 Virtual Environment: 
```python3 -m venv env```

Activate Virtual Environment:
```source env/bin/activate```

Deactivate Virtual Environment:
```deactivate```

Remove Virtual Environment:
```sudo em -rf venv```

---
#### Requirements.txt
Automagically create a requirements.txt file:
```pip3 freeze > requirements.txt```