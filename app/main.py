from flask import Flask, request, jsonify
from app.models import init_db, SessionManager
import os

app = Flask(__name__)

# Initialize database
init_db()

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint para receber mensagens do WhatsApp
    """
    data = request.json
    
    # Extrair informações básicas da mensagem (ajustar conforme a API usada)
    # Exemplo genérico para Meta Cloud API / Evolution API
    try:
        if 'messages' in data: # Meta Cloud API
            message = data['messages'][0]
            phone_number = message['from']
            text = message.get('text', {}).get('body', '')
        elif 'data' in data: # Evolution API style
            phone_number = data['data']['key']['remoteJid'].split('@')[0]
            text = data['data']['message'].get('conversation', '')
        else:
            # Fallback ou erro de formato
            return jsonify({"status": "ignored"}), 200
    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        return jsonify({"status": "error"}), 400

    from app.bot_logic import handle_message
    handle_message(phone_number, text)
    
    return jsonify({"status": "success"}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
