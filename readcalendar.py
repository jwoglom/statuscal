from gcsa.google_calendar import GoogleCalendar

import datetime

def get_calendar(calendar_id, path):
    return GoogleCalendar(calendar=calendar_id, credentials_path=path)

def event_to_json(event, calendar_name):
    return {
        'attendees': sorted([{
                'display_name': a.display_name,
                'email': a.email,
                'response_status': a.response_status
            } for a in event.attendees], key=lambda a: a['response_status']),
        'color_id': event.color_id,
        'description': event.description,
        'end': event.end,
        'id': event.id,
        'location': event.location,
        'other': event.other,
        'recurrence': event.recurrence,
        'reminders': [{
                'method': r.method,
                'minutes_before_start': r.minutes_before_start
            } for r in event.reminders],
        'start': event.start,
        'summary': event.summary,
        'timezone': event.timezone,
        'calendar_name': calendar_name,
    }

def get_calendar_events(credentials_config, max_days=-1):
    time_max = (datetime.datetime.now() + datetime.timedelta(days=max_days)) if max_days > 0 else None

    events = []
    for config in credentials_config:
        cid = config['calendar_id'] if 'calendar_id' in config else 'primary'
        name = config['calendar_name'] if 'calendar_name' in config else None
        json = '{}/credentials.json'.format(config['credentials_path'])

        calendar = get_calendar(cid, json)
        for event in calendar.get_events(time_max=time_max):
            events.append(event_to_json(event, calendar_name=name))

    def to_datetime(d):
        if type(d) == datetime.date:
            return datetime.datetime.combine(d, datetime.datetime.min.time())

        if d is None:
            return datetime.datetime(2000,1,1)
        return d

    events.sort(key=lambda e: to_datetime(e['start']).replace(tzinfo=None))
    return events
