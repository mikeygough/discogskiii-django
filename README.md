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
* __DONE__ - Price and Quantity Order Books, for example:

    |  Price  | Offer Qty. | Offer Quality |
    | :-----: | ---------: | :------------ |
    | 500     | 1          | M             |
    | 400     | 1          | NM            |
    | 300     | 1          | VG +          |
    | 300     | 1          | VG            |
    | 200     | 1          |               |
    | 100     | 1          |               |

* __DONE__ - Artist Releases Dashboard
* __DONE__ - User Watchlist

    * Add row removal animation when user removes market from saved markets
    
* __DONE__ - Tailwind CSS Styling
* __DONE__ - Artist Release Sorting
* __Subscribe to Market__ - I see this as a kind of challenge feature because I'm really not sure how to build it. I'd like a user to be able to subscribe to a market and receive updates when that market changes. I.E. a new offer is placed in the market. I think that [Django has their own email service](https://docs.djangoproject.com/en/4.2/topics/email/).
* __Market Statistics__ - See new listings, order books with the highest price, lowest price, most orders, etc.
Thinking through the implementation of this feature... How am I going to get all the data I'll need? It's probably too many requests to try and get all release statistics for every release by an artist... Even if I were to cache them all, it would probably take too long to spin up. What are my other options? I guess the stats I can reliable get are ones available via the API (as opposed to scraping). These include:
    
    * release stats: num_have, num_want
    * marketplace release stats: lowest_price, num_for_sale

    One sample statistic I could use is getting the lowest_price for each of the records available for sale by an artist. It wouldn't include anything about the quality of the records but I could at least link to the marketplace page for that record from there.
    
    I have an idea to make this better... Rather than slowing everything down by trying to get the sale information for every record, I don't have to! First I can just make a request to check if there are any for sale... Then of those available for sale I can see the listing information... How many Sun Ra original pressings might be available at any given time? My guess is not too many... That's why they're original pressings and rare!

* __Multiple Device Optimations__ - App should render and function flawlessly on all device types.
* __React Components__ - Implement at least one React component! But I might kick this down the road since it may be more beneficial to finish my React course before I start slinging around sloppy code.


<br>

---

<br>

### Design
For the first version of this design I'm imagining a home screen with labels for each of the available artist markets. These are statically defined by me and just include the artist. For example, statically defined artist markets could be ["Sun Ra", "John Coltrane", "Miles Davis", "Alice Coltrane"]. These are completely arbitrary and just exist to help me flesh out a more scalable design. -- I'm having trouble reworking this concept now that it's mapped in my mind. Thus, it is the current implementation and has been since inception.

When a use clicks on an artist market, they're taken to a page that displays all of that artists records, sorted chronologically. Currently, this is a small performance bottleneck since on each page load I'm requesting all of this data from Discogs servers. For an artist like Miles Davis who has hundreds of records, this results in a multi-second page load. -- This bottleneck has been (partially) addressed. Now I'm doing the entire db initialization feature on the /index page load. Thus, it takes several minutes to request all the data if a user is running the app for the first time. But, it results in quicker subsequent page loads of the /artist-releases route.

Since it's very rare for these artist (all of whom are now deceased) to release new records, I've to created a Django model for each artist. That model stores all of the records they've produced along with the information I need to load the page. It will be much faster to load the page this way, and since these arists aren't launching new records I should be safe to only have to fetch this once from Discogs. Just in case, I can run a quick check once a month or something and compare my DB with Discogs looking at page numbers or some other metric. Miles Davis, for example had a 'new' release in 2023. -- I've implemented caching as best I can.

Clicking into a market will then reveal the orderbook, more specifically the number and prices of original pressings available for sale.

<br>

#### Color Palette
Primary Color:
* __bg-gradient-to-r from-yellow-400 to-yellow-600__: This gradient will serve as the primary color, providing a warm and inviting tone.


Secondary Colors:
* __bg-gradient-to-r from-gray-100 to-gray-300__: This gradient will serve as a light secondary color, providing a subtle contrast and a clean aesthetic.
* __bg-gradient-to-r from-gray-700 to-gray-900__: This gradient will serve as a dark secondary color, offering depth and sophistication.


Neutral Color:
* __bg-white__: This light color will be used as a neutral background, creating a sense of openness and simplicity.


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


I may have discovered an additional factor for determining the value of original pressings. Discogs provides community metrics for each release. Two such metrics are community_have and community_want. Using these we can construct a community "demand score", community_want / community_have. Just eye-balling the data for Alice Coltrane, for example, there appears to be a positive relationship between demand score and lowest_selling price. This could be interesting data to place on a statistics page.

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

Create User:

For most applications a simple user model will do. This can be extended later. For example, in models.py:

```
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass
```

Then be sure to add this model to _PROJECT_NAME/settings.py_ like this:

```
AUTH_USER_MODEL = "APP_NAME.User"
```



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

### JavsScript

Helpful JavsScript Snippets

Presented with a bunch of buttons that have data-color attributes (data-color="red", for example),
upon clicking change the style of the h1 tag who's id is #hello to that button's particular data-color.
```
document.addEventListener('DOMContentLoaded', function() {

    document.querySelectorAll('button').forEach(function(button) {
        button.onclick = function() {
            document.querySelector('#hello').style.color = button.datasest.color;
        }
    })
})
```

Arrow Notation (Same as Above)
```
document.addEventListener('DOMContentLoaded', () => {

    document.querySelectorAll('button').forEach(button => {
        button.onclick = function() {
            document.querySelector('#hello').style.color = button.datasest.color;
        }
    })
})
```

Given a form submit, create a list item and append it to the unordered list with id of #tasks. We select elements by their IDs
```
document.addEventListener('DOMContentLoaded', () => {

    // by default, disable submit button
    document.querySelector('#submit').disabled = true;

    // enable it when the user types something into the input field.
    document.querySelector('#tasks').onkeyup = () => {
        if (document.querySelector('#task').value.length > 0) {
            document.querySelector('#submit').disabled = false;
        } else {
            document.querySelector('#submit').disabled = true;    
        }

    }

    document.querySelector('form').onsubmit = () => {
        const task = document.querySelector('#task').value;

        const li = document.createElement('li');
        li .innerHTML = task;

        document.querySelector('#tasks').append(li);

        // clear out the value of the input field
        document.querySelector('#task').value = '';
        // disable submit button again
        document.querySelector('#submit').disabled = true;

        // stop form from submitting
        return false;
    }
})
```

Local Storage
```
localStorage.getItem(key)
localStorage.setItem(key, value)
```

AJAX: Asynchronous requests without a page load (just tie to a form submit)
```
document.addEventListener('DOMContentLoaded', function() {

    // fetch returns a promise... something will come back but maybe not immediately
    fetch('EXAMPLE_URL')
    .then(response => return response.json())
    .then(data => {
        console.log(data);
    })
    // if something goes wrong, catch error
    .catch(error => {
        consol.log('Error:', error);
    });

});
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

```git push```

Branching

See Branches

```git branch```

Create New Branch & Checkout

```git checkout -b BRANCH_NAME```

While on Main, Merge in New Branch

```git merge BRANCH_NAME```

Delete Branch

```git branch -d BRANCH_NAME```