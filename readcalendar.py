from typing import List
from gcsa.google_calendar import GoogleCalendar
from google_auth_oauthlib.flow import InstalledAppFlow, _RedirectWSGIApp, _WSGIRequestHandler, InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

import pickle
import google
import os
import json
import wsgiref.simple_server
import wsgiref.util
import webbrowser



import datetime

def gcal_credentials(
        credentials_path: str = None,
        token_path: str = None,
        save_token: bool = True,
        read_only: bool = False
    ):
    credentials_path = credentials_path or GoogleCalendar._get_default_credentials_path()
    credentials_dir, credentials_file = os.path.split(credentials_path)
    token_path = token_path or os.path.join(credentials_dir, 'token.pickle')
    scopes = [GoogleCalendar._READ_WRITE_SCOPES + ('.readonly' if read_only else '')]

    authentication_flow_host = os.getenv('AUTH_FLOW_HOST')
    authentication_flow_port = int(os.getenv('AUTH_FLOW_PORT', 8080))

    def _run_local_server(
        flow,
        host="localhost",
        port=8080,
        authorization_prompt_message=InstalledAppFlow._DEFAULT_AUTH_PROMPT_MESSAGE,
        success_message=InstalledAppFlow._DEFAULT_WEB_SUCCESS_MESSAGE,
        open_browser=True,
        redirect_uri_trailing_slash=True,
        **kwargs
    ):
        wsgi_app = _RedirectWSGIApp(success_message)
        # Fail fast if the address is occupied
        wsgiref.simple_server.WSGIServer.allow_reuse_address = False
        local_server = wsgiref.simple_server.make_server(
            'localhost', port, wsgi_app, handler_class=_WSGIRequestHandler
        )

        redirect_uri_format = (
            "http://{}:{}/" if redirect_uri_trailing_slash else "http://{}:{}"
        )
        flow.redirect_uri = redirect_uri_format.format(host, local_server.server_port)
        auth_url, _ = flow.authorization_url(**kwargs)

        if open_browser:
            webbrowser.open(auth_url, new=1, autoraise=True)

        print(authorization_prompt_message.format(url=auth_url))

        local_server.handle_request()

        # Note: using https here because oauthlib is very picky that
        # OAuth 2.0 should only occur over https.
        authorization_response = wsgi_app.last_request_uri.replace("http", "https")
        flow.fetch_token(authorization_response=authorization_response)

        # This closes the socket
        local_server.server_close()

        return flow.credentials

    def _get_credentials(
            token_path: str,
            credentials_dir: str,
            credentials_file: str,
            scopes: List[str],
            save_token: bool,
            host: str,
            port: int
    ) -> Credentials:
        credentials = None

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token_file:
                credentials = pickle.load(token_file)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                credentials_path = os.path.join(credentials_dir, credentials_file)
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes, redirect_uri=os.getenv('AUTH_REDIRECT_URI'))
                credentials = _run_local_server(flow, host=host, port=port, open_browser=False, redirect_uri_trailing_slash=False, access_type=None)

            if save_token:
                with open(token_path, 'wb') as token_file:
                    pickle.dump(credentials, token_file)

        return credentials

    return _get_credentials(
        token_path,
        credentials_dir,
        credentials_file,
        scopes,
        save_token,
        authentication_flow_host,
        authentication_flow_port
    )

def get_calendar(calendar_id, path):
    try:
        return GoogleCalendar(calendar=calendar_id, credentials_path=path, credentials=gcal_credentials(credentials_path=path))
    except google.auth.exceptions.RefreshError as e:
        raise RuntimeError('Please delete {} and restart to re-authenticate with Google Calendar'.format(path.replace('credentials.json','token.pickle'))) from e

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
        for event in calendar.get_events(time_max=time_max, single_events=True):
            events.append(event_to_json(event, calendar_name=name))

    def to_datetime(d):
        if type(d) == datetime.date:
            return datetime.datetime.combine(d, datetime.datetime.min.time())

        if d is None:
            return datetime.datetime(2000,1,1)
        return d

    events.sort(key=lambda e: to_datetime(e['start']).replace(tzinfo=None))
    return events
