import psutil
import time

# Lista de nombres de navegadores comunes (Windows)
browsers = ["chrome.exe", "firefox.exe", "msedge.exe", "brave.exe"]

# Estado anterior: navegador abierto o cerrado
previous_state = False

def is_browser_open():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() in browsers:
            return True
    return False

print("Monitoreando estado del navegador...")

while True:
    current_state = is_browser_open()

    if current_state and not previous_state:
        print("🔵 Navegador abierto")
    elif not current_state and previous_state:
        print("🔴 Navegador cerrado")

    previous_state = current_state
    time.sleep(2)  # Comprobación cada 2 segundos
