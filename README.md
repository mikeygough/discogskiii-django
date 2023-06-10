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
The goal of this project is... to build a a lower level trading interface for those interested in the market for original pressing vinyl records.

I imagine a user being presented with a simple order book for a particular pressing. Much in the same way that stock, crypto, and derivative markets are displayed on a screen.

In the current model, if a user is interested in a particular record they first have to search it. After finding that record, they need to locate the master copy. The master copy contains information about all pressings of that music. From there, the user has to find the earliest listed pressing for that record. Then, they can see if any are available for sale.

If there are any for sale, they have to filter through those which are available. Each has a price, condition and seller. It's not uncommon for two listings of the same record to be priced wildly far from each other. Perhaps Seller A wanted $1,000. But Seller B has the same record, enters the market, and offers $800. This friction in the price discovery process makes it more difficult for sellers can hit a bid and buyers to determine fair value.

If there are no records of the original listing for sale then the user wasted their time. Additionally, there is no way for them to know when a pressing of that record becomes available for sale other than by constantly refreshing new listings in the marketplace.

<br>

---

<br>

### Features
Features I would like to include in the project:
* Price and Quantity order books colored by quality for every jazz original pressing. I might want to to tweak this design to better represent quality. For now I am using two rows for the same price but separate qualities. This table representation is also using an additional column for the quality rating, this may be expressed more clearly with colors. For example:

    | Bid Qty. |  Price  | Offer Qty. | Offer Quality |
    | :------- | :-----: | ---------: | :------------ |
    |          | 500     | 1          | M             |
    |          | 400     | 1          | NM            |
    |          | 300     | 1          | VG +          |
    |          | 300     | 1          | VG            |
    | 3        | 200     |            |               |
    | 2        | 100     |            |               |

* Artist catalogue search. If a user is interested in Sun Ra, they should be able to search for him and see all original pressings. They should be able to quickly discern which original pressings have 'active markets' (at least one offer). Maybe this is implemented with a simple green dot or flag.
* Create watchlist. User's should be able to save a market to their watchlist to quickly reference it later.
* Subscribe to market... I see this as a kind of challenge feature because I'm really not sure how to build it. I'd like a user to be able to subscribe to a market and receive updates when that market changes. I.E. a new offer is placed in the market.


<br>

---

<br>

### Design
For the first version of this design I'm imagining a home screen with labels for each of the available artist markets. These are statically defined by me and just include the artist. For example, currently the statically defined artist markets are ["Sun Ra", "John Coltrane", "Miles Davis", "Alice Coltrane"]. These are completely arbitrary and just exist to help me flesh out a more scalable design.

When a use clicks on an artist market, they're taken to a page that displays all of that artists records, sorted chronologically. Currently, this is a small performance bottleneck since on each page load I'm requesting all of this data from Discogs servers. For an artist like Miles Davis who has hundreds of records, this results in a multi-second page load.

Since it's very rare for these artist (all of whom are now deceased) to release new records, I'm going to create a Django model for each artist. That model will store all of the records they've produced along with the information I need to load the page. It will be much faster to load the page this way, and since these arists aren't launching new records I should be safe to only have to fetch this once from Discogs. Just in case, I can run a quick check once a month or something and compare my DB with Discogs looking at page numbers or some other metric. Miles Davis, for example had a 'new' release in 2023.

Since I'll be fetching page information from my own Database, this means I can add a column to this massive markets table for how many of the original pressing are available for sale. That's achieved with this simple Get request /marketplace/stats/{release_id}{?curr_abbr} which returns the number of that specific release available for sale along with some other information.

Clicking into a market will then reveal the orderbook. Back on the artist markets page I'd like to add support for data filtering and sorting. Currently records are sorted chronologically but this doesn't do much for a trader. It'd be better to choose markets with more than 1 offer, or highest price, etc.


<br>

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

__Notes__

There's a bit of vernacular which is helpful to understand when working with this API:

* __master_id__: represents the album as an entity. there can be multiple release's from a master.

* __release_id__: represents a specific pressing of the master.

* __main_id__: represents the original pressing of the master.

* __listing_id__: represents a marketplace listing of a release. unlike master, release, or main, these can appear and dissapear as records are bought and sold.

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

After creating models:

Make Migrations:

```python manage.py makemigrations```

Apply Migrations:

```python manage.py migrate```

Activate the Django Python Shell

```python manage.py shell```

Create Admin:

```python manage.py createsuperuser```

After creating an Admin:

* Add models to admin.py
    * from .models import MODEL_NAME
    * admin.site.register(MODEL_NAME)
* Visit BASE_URL/admin

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

### Tailwind CSS

This was kind of a pain to setup 😅 But I've been wanting to try [Tailwind CSS](https://tailwindcss.com/) for a while now! I followed along with [this tutorial](https://www.youtube.com/watch?v=lsQVukhwpqQ) and got everything up and running!

Run the NPM Dev Server (to auto-load css)

```npm run dev```

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