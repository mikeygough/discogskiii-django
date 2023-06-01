# discogskiii-django
a web app and order book for vinyl records available for sale on discogs!



<br>


## Reference:

---
### Django
Install Django:

```pip3 install Django```

Create Project:

```django-admin startproject PROJECT_NAME```

Run Server:

```python manage.py runserver```

Create App:

```python manage.py startapp APP_NAME```


After creating a new app:

* Add APP_NAME to _PROJECT_NAME/settings.py_ installed_apps list
* Add APP_NAME to urlpatterns in _PROJECT_NAME/urls.py_
* Add urls.py file to _PROJECT_NAME/APP_NAME_

<br>
Add HTML:

Create PROJECT_NAME/APP_NAME/templates/APP_NAME/index.html

<br>

---
### Django HTML Templating
Insert Variable:
```
{{ VARIABLE }}
```
Add Logic:
```
{% if CONDITION %}
    
    Some HTML
    
{% else %}
    
    Some other HTML

{% endif %}
```
Loop:
```
{% for item in items %}

    Some HTML with {{ item }}

{% endfor %}
```

Add CSS to an HTML file:

_sometimes you need to restart the server to load static files_
```
{% load static %}

<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Welcome to Discogskiii</title>
        <link href="{% static 'APP_NAME/styles.css' %}" rel="stylesheet">
    </head>
    <body>
        <h1>Hello, vinyl heads!</h1>
    </body>
</html>
```


<br>

---
### Virtual Environments
Create Python3 Virtual Environment:

```python3 -m venv env```

Activate Virtual Environment:

```source env/bin/activate```

Deactivate Virtual Environment:

```deactivate```

Remove Virtual Environment:

```sudo em -rf venv```

<br>

---
### Requirements.txt
Automagically create a requirements.txt file:

```pip3 freeze > requirements.txt```