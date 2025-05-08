from pynput.keyboard import Key, Listener
import threading
import time

# Configuración: tiempo entre capturas en minutos
intervalo_minutos = 15  # Puedes cambiar este valor

# Bandera para evitar múltiples capturas simultáneas
capturando = False

# Función que se ejecuta periódicamente
def capturar_teclas():
    global capturando

    if capturando:
        return  # Ya se está capturando, evita múltiples hilos

    capturando = True
    print(f"[{time.strftime('%H:%M:%S')}] Iniciando captura de teclas...")

    def on_press(key):
        print(f"Tecla presionada: {key}")

    def on_release(key):
        # Puedes detener la captura tras cierta tecla, si quieres
        pass

    # Captura por un tiempo limitado
    listener = Listener(on_press=on_press, on_release=on_release)
    listener.start()

    # Capturar durante X segundos (ej. 10 segundos)
    tiempo_captura = 900
    time.sleep(tiempo_captura)

    listener.stop()
    print(f"[{time.strftime('%H:%M:%S')}] Fin de captura.")
    capturando = False

# Ejecutar la función cada X minutos
def planificador():
    while True:
        capturar_teclas()
        time.sleep(intervalo_minutos * 60)

# Inicia el planificador en segundo plano
threading.Thread(target=planificador, daemon=True).start()

# Mantiene vivo el programa principal
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Programa terminado por el usuario.")
