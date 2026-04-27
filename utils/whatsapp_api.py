import requests
import os
from dotenv import load_dotenv

load_dotenv()

class WhatsAppAPI:
    def __init__(self):
        self.api_url = os.getenv('WHATSAPP_API_URL')
        self.api_key = os.getenv('WHATSAPP_API_KEY')
        self.instance_id = os.getenv('WHATSAPP_INSTANCE_ID')

    def send_message(self, to, text):
        """
        Envia uma mensagem de texto via API do WhatsApp.
        Exemplo baseado na Evolution API.
        """
        if not self.api_url:
            print(f"SIMULAÇÃO WHATSAPP para {to}: {text}")
            return True

        url = f"{self.api_url}/message/sendText/{self.instance_id}"
        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "number": to,
            "text": text,
            "delay": 1200,
            "linkPreview": False
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Erro ao enviar mensagem via WhatsApp: {e}")
            return False
