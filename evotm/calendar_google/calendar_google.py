# https://developers.google.com/calendar/quickstart/python

from __future__ import print_function
from datetime import datetime, timedelta
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from os import path, environ

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarGoogle:
    def __init__(self, tm_home, time_zone):
        self.home      = tm_home
        self.time_zone = time_zone
        self.conn = self.calendar_connection()

    def calendar_connection(self):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        CREDENTIALS_FILE = path.join(self.home,"credentials.json")
        TOKEN_FILE = path.join(self.home,"token.pickle")
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        service = build('calendar', 'v3', credentials=creds)
        return service


    def list_events(self):
        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting List of 10 events')
        events_result = self.conn.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])


    def list_calendars(self):
        # Call the Calendar API
        print('Getting list of calendars')
        calendars_result = self.conn.calendarList().list().execute()

        calendars = calendars_result.get('items', [])

        if not calendars:
            print('No calendars found.')
        for calendar in calendars:
            summary = calendar['summary']
            id = calendar['id']
            primary = "Primary" if calendar.get('primary') else ""
            print("%s\t%s\t%s" % (summary, id, primary))


    def create_event(self, task, start_time, end_time):
        # add task to google calendar
        print(start_time, end_time)
        event_result = self.conn.events().insert(calendarId='primary',
            body={ 
                "summary": task, 
                "description": '',
                "start": {"dateTime": start_time, "timeZone": self.time_zone}, 
                "end": {"dateTime": end_time, "timeZone": self.time_zone},
            }
        ).execute()

        print("created event")
        print("id: ", event_result['id'])
        print("summary: ", event_result['summary'])
        print("starts at: ", event_result['start']['dateTime'])
        print("ends at: ", event_result['end']['dateTime'])

    def update_event():
        # update the event to tomorrow 9 AM IST

        d = datetime.now().date()
        tomorrow = datetime(d.year, d.month, d.day, 9)+timedelta(days=1)
        start = tomorrow.isoformat()
        end = (tomorrow + timedelta(hours=2)).isoformat()

        event_result = self.conn.events().update(
            calendarId='primary',
            eventId='4qnt0okd4dmr0hik3mh073qnls',
            body={ 
                "summary": 'Updated Automating calendar',
                "description": 'This is a tutorial example of automating google calendar with python, updated time.',
                "start": {"dateTime": start, "timeZone": self.time_zone}, 
                "end": {"dateTime": end, "timeZone": self.time_zone},
            },
        ).execute()

        print("updated event")
        print("id: ", event_result['id'])
        print("summary: ", event_result['summary'])
        print("starts at: ", event_result['start']['dateTime'])
        print("ends at: ", event_result['end']['dateTime'])

    def delete_event(self):
        # Delete the event
        try:
            self.conn.events().delete(
                calendarId='primary',
                eventId='4qnt0okd4dmr0hik3mh073qnls',
            ).execute()
        except googleapiclient.errors.HttpError:
            print("Failed to delete event")
        
        print("Event deleted")


if __name__ == '__main__':
    cal = CalendarGoogle()
    cal.list_events()
