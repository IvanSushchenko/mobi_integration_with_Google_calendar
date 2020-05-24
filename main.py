import requests
from bs4 import BeautifulSoup as bs
import json
from datetime import *
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
import pytz
import re

settings_file = "settings.json"


class Mobi:
    # Import settings
    with open(settings_file) as file:
        settings = (json.load(file))["mobi_settings"]

    with open(settings["credentials_file"]) as file:
        credentials = json.load(file)
    with requests.Session() as mobi_session:
        authenticated = mobi_session.post(settings["main_url"], data=credentials["mobi"])

    def get_page(self, url):
        response = self.mobi_session.get(url)
        page = bs(response.text, "html.parser")
        return page

    def refactor_plan_data(self, plan):
        refactored_plan = []
        for lesson in plan:
            for lesson_data in lesson.items():
                date = lesson_data[0]
                lesson_info = lesson_data[1].split("<br />")
                time_range = lesson_info[0].split(" - ")
                time_start = (datetime.strptime(date + time_range[0], "%Y-%m-%d%H:%M")).astimezone(pytz.timezone("Europe/Warsaw")).isoformat()
                time_end = (datetime.strptime(date + time_range[1], "%Y-%m-%d%H:%M")).astimezone(pytz.timezone("Europe/Warsaw")).isoformat()
                summary = lesson_info[1]
                lecturer_auditorium = (lesson_info[2].split("- ", 1))[1]
                auditorium = (re.search("\((.*)\)", lecturer_auditorium).group(1))
                lesson_refactored_info = {"time_start": time_start, "time_end": time_end, "summary": summary,
                                          "lecturer_auditorium": lecturer_auditorium, "auditorium": auditorium}
                refactored_plan.append(lesson_refactored_info)
        return refactored_plan

    def get_plan(self, week_range):
        plan = []
        days_aliases = ["0.5", "20.5", "40.5", "60.5", "80.5"]
        week_range = dict(zip(days_aliases, week_range))
        start_date = list(week_range.values())[0]
        page = self.get_page(self.settings["plan_url"] + start_date)
        week_plan = page.findAll("div", class_="bx pz tooltip")
        for lesson in week_plan:
            current_day = str((((lesson.get("style")).split("left:"))[1]).replace("%;", ""))
            date = week_range.get(current_day)
            plan.append({date: lesson.get("title")})
        refactored_plan = self.refactor_plan_data(plan)
        return refactored_plan


class Google_Calendar:
    # Import settings
    with open(settings_file) as file:
        settings = (json.load(file))["google_settings"]

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    # Check if token already exist in dir
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(settings["credentials_file"], SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    ### create session
    client = build('calendar', 'v3', credentials=creds)

    def get_calendar_id(self):
        existing_calendars = {}
        while True:
            calendar_list = (self.client.calendarList().list().execute())["items"]
            print("Existing calendars:")
            for calendar in calendar_list:
                existing_calendars[calendar["summary"]] = calendar["id"]
                print(" - ", calendar["summary"])
            calendar_name = input(
                "\nPlease enter calendar name. \nIf you want to create new calendar, just enter new name \nName: ")
            if calendar_name in existing_calendars:
                calendar_id = existing_calendars[calendar_name]
                return calendar_id
            else:
                new_calendar = input("No such calendar, do you want to create new one? (Y or N)\n: ")
                if new_calendar.lower() == "y":
                    # new calendar body
                    calendar_body = {
                        'summary': calendar_name,
                        'timeZone': 'Europe/Warsaw'
                    }
                    calendar_id = (self.client.calendars().insert(body=calendar_body).execute())["id"]
                    return calendar_id
                elif new_calendar.lower() == "n":
                    pass

    def get_planned_events(self, calendar_id, week_range):
        planned_event_dict = {}
        date_min = str((datetime.strptime(list(week_range.keys())[0], "%Y-%m-%d").astimezone()).isoformat())
        date_max = str((datetime.strptime(list(week_range.keys())[-1], "%Y-%m-%d").astimezone()).isoformat())
        planned_event_list = (self.client.events().list(calendarId=calendar_id, timeMin=date_min, timeMax=date_max).execute())["items"]
        for event in planned_event_list:
            planned_event_dict[event["start"]["dateTime"]] = event["summary"]
        return planned_event_dict

    def create_json_event(self, event_data):
        event = {
            'summary': "({auditorium}) - {summary}".format(auditorium=event_data["auditorium"],
                                                           summary=event_data["summary"]),
            'location': 'ZSŁ',
            'description': "{summary} - {lecturer_auditorium}".format(summary=event_data["summary"],
                                                                      lecturer_auditorium=event_data[
                                                                          "lecturer_auditorium"]),
            'start': {
                'dateTime': event_data["time_start"],
                'timeZone': 'Europe/Warsaw',
            },
            'end': {
                'dateTime': event_data["time_end"],
                'timeZone': 'Europe/Warsaw',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 5}
                ],
            },
        }
        return event

    def create_event(self, event_json, calendar_id):
        self.client.events().insert(calendarId=calendar_id, body=event_json).execute()


class App:

    def get_week_range(self, current_week):
        week_range = {}
        additional_weeks = timedelta(days=current_week * 7)
        week_start = datetime.today() - timedelta(days=datetime.today().weekday()) + additional_weeks
        for day in range(0, 5):
            current_day = week_start + timedelta(days=day)
            week_range[current_day.strftime("%Y-%m-%d")] = []
        return week_range

    def compare_plans(self, new_plan, existing_plan):
        print("MOBI: ", new_plan)
        print("GOOGLE: ", existing_plan)
        for event in existing_plan:
            print(event)



def main():
    # Import settings
    with open(settings_file) as file:
        settings = (json.load(file))["app_settings"]
    app = App()
    google = Google_Calendar()
    mobi = Mobi()
    calendar_id = google.get_calendar_id()
    print(calendar_id)
    print("Wait, creating events ...")
    for current_week in range(settings["week_limit"]):
        week_range = app.get_week_range(current_week)
        new_plan = mobi.get_plan(week_range)
        #existing_plan = google.get_planned_events(calendar_id, week_range)
        #plan_changes = app.compare_plans(new_plan, existing_plan)
        for lesson in new_plan:
            event_json = google.create_json_event(lesson)
            google.create_event(event_json, calendar_id)
    print("Done")


if __name__ == '__main__':
    main()