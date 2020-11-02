# statuscal

Statuscal is a simple calendar widget which is designed to be used with [statusboard](https://github.com/jwoglom/statusboard). 
It supports multiple calendars on multiple Google accounts across different people, all on one instance.

## Demo

Statuscal provides a touch-friendly user interface for quickly viewing your upcoming calendar items.
On a single statuscal "board", you can see multiple different calendars spanning multiple Google accounts.

<img src="demo/statuscal-demo-1.gif" title="Animated GIF showing how you can click on statuscal entries to view more information about them" height=300 />

To view more information on a calendar entry, you can just click it.
Otherwise, you just see the title of each calendar entry along with the time until the event begins, or time remaining in the event if it is in progress.

The color of each event is determined by the amount of time until it occurs.
This allows you to, at a glance, tell whether you have calendar events starting soon.

<img src="demo/statuscal-demo-2.gif" title="Animated GIF showing how background colors on events change over time depending on how long there is before the event" height=300 />

Events start green, when the start time of the event is more than 4 hours from now, and turn to red when the event's start time gets closer.
As the event progresses, it gets greener until the scheduled end time is reached.

## Setup

Clone the repository and install from requirements.txt or Pipfile:

```bash
pip install -r requirements.txt
  <or>
pipenv install
```

Follow the [Getting Started instructions for google-calendar-simple-api](https://google-calendar-simple-api.readthedocs.io/en/latest/getting_started.html) to configure Google Calendar API credentials.

Once you have a `credentials.json` file, create a folder inside `credentials` to put it in, e.g.:

```bash
mkdir -p credentials/personal
mv ~/Downloads/credentials.json credentials/person_one_personal/
```

Now you can begin to configure your statuscal "boards".
A statuscal board represents all of the different calendars which will be displayed at a given URL.
This allows you to have multiple different "boards" which represent different people's calendars.

Assume that person_one wants to display three different calendars on their board at `http://statuscal_url/person_one`:

 * A primary calendar (on their personal Google account)
 * A shared calendar (on their personal Google account)
 * A work calendar (on their work Google account)

And that person_two wants to display a single calendar on their board at `http://statuscal_url/person_two`:

 * A primary calendar (on their personal Google account)

They could configure their board settings with the following configuration in `config.py`:

```python
boards = {
    # This is a statuscal board which is visible at /person_one, and displays
    # events from all of the given calendars:
    'person_one': [
        {
            # A calendar to be displayed on the board
            'calendar_name': 'My Calendar',
            # 'primary' references the default calendar for the user
            'calendar_id': 'primary',
            # The folder with credentials for a user account with access to this calendar.
            'credentials_path': 'credentials/person_one_personal',
        },
        {
            # A different calendar which the same user has access to
            'calendar_name': 'My Shared Calendar',
            # Either an email address or Calendar ID
            'calendar_id': 'calendar_id',
            'credentials_path': 'credentials/person_one_personal',
        },
        {
            # A different calendar with separate Google account credentials
            'calendar_name': 'My Work Calendar',
            'calendar_id': 'primary',
            'credentials_path': 'credentials/person_one_work',
        }
    ],
    # An entirely different statuscal board for a different person
    'person_two': [
        {
            'calendar_name': 'Person Two Calendar',
            'calendar_id': 'primary',
            'credentials_path': 'credentials/person_two',
        },
    ]
}
```

Now, simply start the Flask server:

```bash
FLASK_APP=app.py flask run
```

In production, you can run the application with Gunicorn inside a virtualenv using a script such as the following:

```bash
source ./venv/bin/activate &&
exec gunicorn --pythonpath ./venv/lib/python3.8/site-packages --worker-class eventlet -w 1 app:app -b 127.0.0.1:8000 --log-level INFO --access-logfile -
```

## Statusboard configuration
Statuscal works great when used as the primary widget for [statusboard](https://github.com/jwoglom/statusboard).
To configure, set the main iframe to the URL of statuscal in the `config.py` of statusboard.
(Depending on the size of your screen, you can also adjust the zoom URL parameter.)

```python
def custom_init_response(message):
    data = {}
    # ...
    data['main_iframe'] = {
        'name': 'statuscal',
        'url': 'http://statuscal_url/person_one?zoom=0.75',
        'scrolling': 'yes'
    }
    # ...
    return data
```