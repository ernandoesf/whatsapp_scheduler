from app.models import SessionManager
from utils.whatsapp_api import WhatsAppAPI
from utils.calendar_api import GoogleCalendar
import datetime

whatsapp = WhatsAppAPI()
# calendar = GoogleCalendar() # Será inicializado sob demanda para evitar problemas de credenciais no boot

def handle_message(phone_number, text):
    text = text.strip().lower()
    session = SessionManager.get_session(phone_number)
    state = session['state']
    data = session['data']

    if text == 'cancelar':
        SessionManager.clear_session(phone_number)
        whatsapp.send_message(phone_number, "Agendamento cancelado. Se precisar de algo, é só chamar!")
        return

    if state == 'START':
        whatsapp.send_message(phone_number, "Olá! 👋 Sou o assistente do eletricista. Vou te ajudar a agendar um atendimento. Qual seu nome?")
        SessionManager.update_session(phone_number, 'AWAITING_NAME', data)

    elif state == 'AWAITING_NAME':
        data['name'] = text.title()
        whatsapp.send_message(phone_number, f"Prazer, {data['name']}! Qual o endereço do atendimento?")
        SessionManager.update_session(phone_number, 'AWAITING_ADDRESS', data)

    elif state == 'AWAITING_ADDRESS':
        data['address'] = text
        whatsapp.send_message(phone_number, "Pode me descrever qual o problema elétrico que está acontecendo?")
        SessionManager.update_session(phone_number, 'AWAITING_DESCRIPTION', data)

    elif state == 'AWAITING_DESCRIPTION':
        data['description'] = text
        whatsapp.send_message(phone_number, "Vou verificar os horários disponíveis na agenda do eletricista... Só um momento.")
        
        try:
            calendar = GoogleCalendar()
            slots = calendar.get_free_slots()
            if not slots:
                whatsapp.send_message(phone_number, "Desculpe, não encontrei horários disponíveis nos próximos dias. Por favor, tente novamente mais tarde.")
                SessionManager.clear_session(phone_number)
                return

            data['slots'] = [s.isoformat() for s in slots]
            
            msg = "Tenho estes horários disponíveis:\n"
            for i, slot in enumerate(slots, 1):
                msg += f"{i}️⃣ {slot.strftime('%A às %H:%M')}\n"
            msg += "\nDigite o número da opção desejada."
            
            whatsapp.send_message(phone_number, msg)
            SessionManager.update_session(phone_number, 'AWAITING_SLOT', data)
        except Exception as e:
            print(f"Erro ao acessar Google Calendar: {e}")
            whatsapp.send_message(phone_number, "Ocorreu um erro ao acessar a agenda. Por favor, tente novamente em alguns instantes.")

    elif state == 'AWAITING_SLOT':
        try:
            choice = int(text) - 1
            if 0 <= choice < len(data['slots']):
                selected_slot_iso = data['slots'][choice]
                selected_slot = datetime.datetime.fromisoformat(selected_slot_iso)
                data['selected_slot'] = selected_slot_iso
                
                msg = f"Confirmando seu agendamento:\n"
                msg += f"📅 Data: {selected_slot.strftime('%d/%m às %H:%M')}\n"
                msg += f"📍 Endereço: {data['address']}\n"
                msg += f"🔧 Serviço: {data['description']}\n\n"
                msg += "Posso confirmar? (sim/não)"
                
                whatsapp.send_message(phone_number, msg)
                SessionManager.update_session(phone_number, 'AWAITING_CONFIRMATION', data)
            else:
                whatsapp.send_message(phone_number, "Opção inválida. Por favor, digite o número correspondente ao horário desejado.")
        except ValueError:
            whatsapp.send_message(phone_number, "Por favor, digite apenas o número da opção.")

    elif state == 'AWAITING_CONFIRMATION':
        if text in ['sim', 's', 'confirmar', 'pode']:
            whatsapp.send_message(phone_number, "Agendando... Por favor, aguarde.")
            
            try:
                calendar = GoogleCalendar()
                start_time = datetime.datetime.fromisoformat(data['selected_slot'])
                end_time = start_time + datetime.timedelta(hours=1)
                
                summary = f"Atendimento Elétrico – {data['name']}"
                description = (
                    f"Nome: {data['name']}\n"
                    f"Endereço: {data['address']}\n"
                    f"Problema: {data['description']}\n"
                    f"Telefone: {phone_number}"
                )
                
                calendar.create_event(summary, description, start_time, end_time)
                
                whatsapp.send_message(phone_number, "✅ Agendamento confirmado!\nO eletricista estará no local no dia e horário combinado.\nObrigado pelo contato!")
                SessionManager.clear_session(phone_number)
            except Exception as e:
                print(f"Erro ao criar evento: {e}")
                whatsapp.send_message(phone_number, "Houve um erro ao confirmar na agenda. Por favor, tente novamente.")
        elif text in ['não', 'nao', 'n']:
            whatsapp.send_message(phone_number, "Tudo bem. Qual horário você prefere? (Digite o número da opção anterior ou 'cancelar')")
            SessionManager.update_session(phone_number, 'AWAITING_SLOT', data)
        else:
            whatsapp.send_message(phone_number, "Por favor, responda apenas 'sim' ou 'não'.")
