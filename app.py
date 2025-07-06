
import json
import time
from datetime import datetime

VENOM_MESSAGES_PATH = 'messages.json'
CONTACTS_PATH = 'contacts.json'

# Cargar contactos
try:
    with open(CONTACTS_PATH, 'r', encoding='utf-8') as f:
        contacts = json.load(f)
except:
    contacts = {}

def load_messages():
    try:
        with open(VENOM_MESSAGES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_messages(messages):
    with open(VENOM_MESSAGES_PATH, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

def es_salida(texto):
    texto = texto.lower()
    return 'salida' in texto or 'sallida' in texto or 'salio' in texto or 'egreso' in texto

def responder_mensaje(numero):
    return "Su mensaje fue recibido por el CMD de Montevideo, si luego de cinco minutos no es contactado el ingreso se considera AUTORIZADO, no olvides informar la salida, gracias."

def procesar():
    print("🟢 Chat Bot activo y monitoreando mensajes de Venom Bot...")
    mensajes_anteriores = []

    while True:
        mensajes = load_messages()
        nuevos = []

        for mensaje in mensajes:
            if not mensaje.get('procesado'):
                numero = mensaje.get('from', '')
                texto = mensaje.get('body', '')

                if not es_salida(texto):
                    # Buscar nombre
                    nombre = contacts.get(numero, numero)
                    mensaje['nombre'] = nombre
                    mensaje['hora'] = datetime.now().strftime('%H:%M:%S')
                    mensaje['procesado'] = True

                    print(f"💬 Procesando mensaje de {nombre}: {texto}")
                    # Simular respuesta automática
                    respuesta = responder_mensaje(numero)
                    print(f"🤖 Respuesta automática enviada: {respuesta}")
                else:
                    mensaje['procesado'] = True
                    print(f"🚪 Mensaje de salida detectado: {texto}")

                nuevos.append(mensaje)

        if nuevos:
            save_messages(mensajes)

        time.sleep(2)

if __name__ == '__main__':
    procesar()
