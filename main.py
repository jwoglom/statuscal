
import os

from flask import Flask, render_template, request, make_response, send_from_directory, abort, jsonify

from readcalendar import get_calendar_events, event_to_json

# To specify custom configurations, look at config_sample.py
try:
    from config import credentials_paths, access_token
except ImportError:
    import secrets

    print('Failed to load custom config')
    credentials_paths = ['credentials/']
    access_token = secrets.token_urlsafe(32)
    print('Random access token set:', access_token)

app = Flask(__name__, static_url_path='/static')

if os.getenv('APPLICATION_ROOT'):
    app.config['APPLICATION_ROOT'] = os.getenv('APPLICATION_ROOT')

cors_origins = '*'
if os.getenv('CORS_ALLOWED_ORIGINS'):
    cors_origins = os.getenv('CORS_ALLOWED_ORIGINS').split(',')

# Log messages with Gunicorn
if not app.debug:
    import logging
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)


@app.route('/<path:token>')
def index(token):
    if token != access_token:
        return abort(403, description='Forbidden')

    return render_template('index.html')

@app.route('/<path:token>/events.json')
def events(token):
    if token != access_token:
        return abort(403, description='Forbidden')

    max_days = request.args.get('max_days', 7)
    events = get_calendar_events(credentials_paths, max_days=max_days)
    data = {"events": list(map(event_to_json, events))}

    return jsonify(data)

@app.route('/static/<path:path>')
def static_path(path):
    return send_from_directory('static', path)