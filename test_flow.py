import sys
import os
import json

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import init_db, SessionManager
from app.bot_logic import handle_message

# Mocking WhatsApp API to avoid real calls during tests
import utils.whatsapp_api
utils.whatsapp_api.WhatsAppAPI.send_message = lambda self, to, text: print(f"\n[BOT -> {to}]: {text}")

# Mocking Google Calendar to avoid real API calls during tests
import utils.calendar_api
from datetime import datetime, timedelta

class MockCalendar:
    def get_free_slots(self, days=5):
        now = datetime.now()
        return [now + timedelta(hours=i+1) for i in range(5)]
    def create_event(self, summary, description, start_time, end_time):
        print(f"\n[CALENDAR]: Evento criado: {summary} em {start_time}")
        return {"id": "mock_event_id"}

utils.calendar_api.GoogleCalendar = MockCalendar

def run_simulation():
    init_db()
    phone = "5511999999999"
    
    print("--- Iniciando Simulação de Atendimento ---")
    
    steps = [
        "oi",                    # Início
        "João Silva",            # Nome
        "Rua das Flores, 123",   # Endereço
        "Troca de disjuntor",    # Descrição
        "1",                     # Escolha do horário
        "sim"                    # Confirmação
    ]
    
    for user_input in steps:
        print(f"\n[USER]: {user_input}")
        handle_message(phone, user_input)

if __name__ == "__main__":
    run_simulation()
