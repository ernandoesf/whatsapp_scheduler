import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendar:
    def __init__(self):
        self.creds = None
        token_path = 'token.json'
        
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Nota: Em produção, o fluxo de autenticação seria diferente (OAuth2 web flow)
                # Para este projeto, assumimos que o usuário fornecerá o credentials.json
                if os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    self.creds = flow.run_local_server(port=0)
                    with open('token.json', 'w') as token:
                        token.write(self.creds.to_json())

        self.service = build('calendar', 'v3', credentials=self.creds)

    def get_free_slots(self, days=5):
        now = datetime.datetime.utcnow()
        start_time = now.isoformat() + 'Z'
        end_time = (now + datetime.timedelta(days=days)).isoformat() + 'Z'

        events_result = self.service.events().list(
            calendarId='primary', timeMin=start_time, timeMax=end_time,
            singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        # Lógica simplificada para encontrar horários (08:00 - 18:00)
        slots = []
        for i in range(days):
            date = (now + datetime.timedelta(days=i)).date()
            if date.weekday() >= 5: # Pular fim de semana
                continue
                
            for hour in [9, 10, 11, 14, 15, 16]: # Horários fixos para simplificar
                slot_start = datetime.datetime.combine(date, datetime.time(hour, 0))
                slot_end = slot_start + datetime.timedelta(hours=1)
                
                if slot_start < now:
                    continue

                is_free = True
                for event in events:
                    e_start = event['start'].get('dateTime', event['start'].get('date'))
                    e_end = event['end'].get('dateTime', event['end'].get('date'))
                    
                    # Converter strings ISO para datetime
                    if 'T' in e_start:
                        e_start_dt = datetime.datetime.fromisoformat(e_start.replace('Z', ''))
                        e_end_dt = datetime.datetime.fromisoformat(e_end.replace('Z', ''))
                        
                        if (slot_start < e_end_dt and slot_end > e_start_dt):
                            is_free = False
                            break
                
                if is_free:
                    slots.append(slot_start)
                    if len(slots) >= 5: # Limitar a 5 opções
                        return slots
        return slots

    def create_event(self, summary, description, start_time, end_time):
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
        }
        event = self.service.events().insert(calendarId='primary', body=event).execute()
        return event
