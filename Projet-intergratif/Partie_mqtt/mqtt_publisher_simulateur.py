# =============================================================================
# mqtt_publisher_simulateur.py
# SAE 2.04 - Collecte de données IoT via MQTT
# Rôle : simuler un capteur en publiant des trames toutes les 5 secondes
# =============================================================================

import random
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# --- Configuration (à modifier selon le besoin) ------------------------------

BROKER = "test.mosquitto.org"
PORT   = 1883

# Topic sur lequel publier (Maison1 ou Maison2)
TOPIC      = "IUT/Colmar2026/SAE2.04/Maison1"

# Identifiant matériel fixe du capteur simulé (adresse MAC fictive)
ID_CAPTEUR = "12A6B8AF6CD3"

# Pièce fixe associée à ce capteur
PIECE      = "sejour"

# Intervalle en secondes entre chaque publication
INTERVALLE = 5

# Plage de température simulée (en °C)
TEMP_MIN = 18.0
TEMP_MAX = 28.0

# --- Génération de la trame --------------------------------------------------

def generer_trame() -> str:
    """
    Génère une trame au format exact imposé par le sujet :
      Id=12A6B8AF6CD3,piece=sejour,date=15/06/2026,heure=12:13:14,temp=26,35

    - La date et l'heure sont dynamiques (valeurs réelles au moment de l'appel).
    - La température est aléatoire entre TEMP_MIN et TEMP_MAX.
    - Le séparateur décimal est une virgule (notation française).
    """
    maintenant  = datetime.now()
    date_str    = maintenant.strftime("%d/%m/%Y")   # ex: 18/06/2026
    heure_str   = maintenant.strftime("%H:%M:%S")   # ex: 14:32:07

    # Température avec 2 décimales, virgule comme séparateur décimal
    temperature = random.uniform(TEMP_MIN, TEMP_MAX)
    temp_str    = f"{temperature:.2f}".replace(".", ",")  # "26.35" -> "26,35"

    trame = f"Id={ID_CAPTEUR},piece={PIECE},date={date_str},heure={heure_str},temp={temp_str}"
    return trame

# --- Callbacks MQTT ----------------------------------------------------------

def on_connect(client, userdata, connect_flags, reason_code, properties):
    """
    Callback appelé quand la connexion au broker est établie (ou échouée).
    """
    if reason_code.is_failure:
        print(f"[ERREUR] Connexion refusée : {reason_code}")
        return

    print(f"[OK] Connecté au broker MQTT (code retour : {reason_code})")
    print(f"[OK] Publication sur le topic : {TOPIC}")
    print(f"[OK] Capteur simulé : ID={ID_CAPTEUR}, pièce={PIECE}")
    print(f"     Envoi toutes les {INTERVALLE} s  |  Temp entre {TEMP_MIN} et {TEMP_MAX} °C")
    print("\n(Ctrl+C pour arrêter)\n")
    print("-" * 60)

# --- Boucle de publication ---------------------------------------------------

def publier_en_boucle(client):
    """
    Publie une trame toutes les INTERVALLE secondes.
    S'arrête proprement sur Ctrl+C (KeyboardInterrupt).
    """
    compteur = 1
    while True:
        trame  = generer_trame()
        result = client.publish(TOPIC, trame, qos=0)

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] #{compteur:03d} Publié  -> {trame}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Erreur publication (code: {result.rc})")

        compteur += 1
        time.sleep(INTERVALLE)

# --- Programme principal -----------------------------------------------------

def main():
    client = mqtt.Client(CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect

    try:
        print(f"Connexion à {BROKER}:{PORT}...")
        client.connect(BROKER, PORT, keepalive=60)

        # loop_start() lance la gestion réseau dans un thread secondaire,
        # ce qui nous permet d'appeler publish() depuis le thread principal.
        client.loop_start()
        time.sleep(1)  # petite pause pour laisser on_connect s'exécuter

        publier_en_boucle(client)

    except KeyboardInterrupt:
        print("\nArrêt demandé par l'utilisateur.")

    except Exception as erreur:
        print(f"[ERREUR] Impossible de joindre {BROKER} : {erreur}")

    finally:
        client.loop_stop()
        client.disconnect()
        print("Déconnecté du broker.")


if __name__ == "__main__":
    main()
