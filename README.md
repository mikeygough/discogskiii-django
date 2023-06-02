# discogskiii-django
Discogskiii is a web app and order book for vinyl records available for sale on [Discogs](https://www.discogs.com/)!

### High-Level Overview
[Discogs](https://www.discogs.com/) is a music database and marketplace.

This app, Discogskiii, is an order book constructor for original pressing vinyl records publicly listed for sale on Discogs.

<br>

---

<br>

### Low-Level Overview
Last year, [According to the Wall Street Journal](https://www.wsj.com/articles/vinyl-records-outsell-cds-for-the-first-time-since-1987-49deeef0), vinyl records outsold CDs for the first time since 1987! After declining for years, maybe the market is back?

In addition to a growing primary market (new pressings and repressings), vinyl also sells actively on the secondary market. 

The market for original pressings is particularly hot for jazz. As an example, Sonny Rollins' record _Saxophone Colossus_, was first release (pressed) in 1957. While a new pressing might cost you $20, an original pressing fetches as much as $300! Both pressings are the same music, but collectors seek original pressings for their rich history as functional art.

<br>

---

<br>

### Project Scope and Goals
The goal of this project is...


---

<br>

### How are Records Priced?
While I have yet to develop an exact model, primary factors influencing secondary market vinyl prices could be:

* __Scarcity__
    * How many were made?
        * Greater scarcity can command a higher price.
    * How many of these originals even still exist?
        * While a painting is subject to damage from sunlight, vinyl records were played! Scratched by a needle! Records are functional pieces of art. While 100 copies may have been pressed in 1957 this does not imply 100 are still available in the world. Some of those original pressings may have been damaged or lost through time.
    * How many of these originals are available for sale?
        * There's a good chance a rare vinyl record is sitting in your families' attic or basement, untentionally limiting the available supply on the market.

* __Popularity of Artist__
    * Some of the most expensive records ever sold were original pressings by groups like Prince, The Beatles, Pink Floyd, and The Velvet Underground.
       * However, this isn't always true. For example, several Sun Ra albums fetch multiple thousands of dollars and he remains largely unknown outside of jazz circles.

* __Vinyl Condition__
   * Discogs uses the [Goldmine Standard](https://support.discogs.com/hc/en-us/articles/360001566193-How-To-Grade-Items) for grading the condition of vinyl records:
      * _Mint (M)_: Absolutely perfect in every way. Certainly never been played, possibly even still sealed.

      * _Near Mint (NM or M-)_: A nearly perfect record. A NM or M- record has more than likely never been played, and the vinyl will play perfectly, with no imperfections during playback.

      * _Very Good Plus (VG+)_: Generally worth 50% of the Near Mint value. A Very Good Plus record will show some signs that it was played and otherwise handled by a previous owner who took good care of it. Defects should be more of a cosmetic nature, not affecting the actual playback as a whole.

      * _Very Good (VG)_: Generally worth 25% of Near Mint value. Many of the defects found in a VG+ record will be more pronounced in a VG disc. Surface noise will be evident upon playing, especially in soft passages and during a song's intro and fade, but will not overpower the music otherwise.

      * _Good (G), Good Plus (G+)_: Generally worth 10-15% of the Near Mint value. A record in Good or Good Plus condition can be played through without skipping. But it will have significant surface noise, scratches, and visible groove wear.

      * _Poor (P), Fair (F)_: Generally worth 0-5% of the Near Mint price. The record is cracked, badly warped, and won't play through without skipping or repeating.

<br>

---

<br>

### Disclaimer
This project represents my submission for a school project and is purely for learning purposes. All data for this project is taken from Discogs via their public API. I ❤️ you Discogs!
<br>

## Reference:

---

<br>

### Discogs
[Discogs API Documentation](https://www.discogs.com/developers)

<br>

---

<br>

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

<br>

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

{% empty %}

    Some other HTML if the iterable is empty

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

Template Inheritance:

Create templates/APP_NAME/layout.html
```
{% load static %}

<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Discogskiii</title>
        <link href="{% static 'APP_NAME/styles.css' %}" rel="stylesheet">
    </head>
    <body>
        {% block body %}
        {% endblock %}
    </body>
</html>
```

Then inherit this layout in other HTML files, for example index.html.
```
{% extends "APP_NAME/layout.html" %}
{% block body %}
    <body>
        <h1>Hello, Discogskiii</h1>
    </body>
{% endblock %}
```

Link to URL:

_where URL_NAME is the name assigned to a path in urls.py and APP_NAME is the variable assigned in that same file._
```
<a href="{% url 'APP_NAME:URL_NAME' %}"> Click Me</a>
```

<br>

---

<br>

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

<br>

### Requirements.txt
Automagically create a requirements.txt file:

```pip3 freeze > requirements.txt```


<br>

---

<br>

### Git
Add Files

```git add```

Commit with Message

```git commit -am "my first commit!"```

Push

```git push"```