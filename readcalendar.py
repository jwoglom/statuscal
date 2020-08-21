from gcsa.google_calendar import GoogleCalendar

import datetime

def get_calendar(path):
    calendar = GoogleCalendar(calendar='primary', credentials_path=path)
    return list(calendar)

def event_to_json(event):
    return {
        'attendees': event.attendees,
        'color_id': event.color_id,
        'description': event.description,
        'end': event.end,
        'id': event.id,
        'location': event.location,
        'other': event.other,
        'recurrence': event.recurrence,
        'reminders': event.reminders,
        'start': event.start,
        'summary': event.summary,
        'timezone': event.timezone
    }

def get_calendar_events(credentials_paths, max_days=-1):
    calendars = [get_calendar(f'{credentials_path}/credentials.json') for credentials_path in credentials_paths]
    events = []
    for cal in calendars:
        for event in cal:
            events.append(event)

    def to_datetime(d):
        if type(d) == datetime.date:
            return datetime.datetime.combine(d, datetime.datetime.min.time())

        return d

    events.sort(key=lambda e: to_datetime(e.start).replace(tzinfo=None))
    if max_days > 0:
        events = filter(lambda e: (to_datetime(e.start).replace(tzinfo=None) - datetime.datetime.now()).days <= max_days, events)
    return events

def main():
    for e in get_calendar_events(['test']):
        print('event:', e.start, '-', e)


if __name__ == '__main__':
    main()