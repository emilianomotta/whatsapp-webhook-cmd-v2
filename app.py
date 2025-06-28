import requests

# Esto simula el número que escribió por WhatsApp
numero = "59894436042"

# Cargar la agenda online
try:
    agenda_url = "https://agenda-web.web.app/data/contacts.json"
    contactos = requests.get(agenda_url).json()
    print("AGENDA:", contactos)

    nombre = contactos.get(numero, None)
    if nombre:
        print("✅ Nombre encontrado:", nombre)
    else:
        print("❌ Nombre no encontrado")

except Exception as e:
    print("💥 Error accediendo a agenda:", e)
