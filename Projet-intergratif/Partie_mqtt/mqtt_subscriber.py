# =============================================================================
# mqtt_subscriber.py
# SAE 2.04 - Collecte de données IoT via MQTT
# Rôle : s'abonner à deux topics, recevoir et parser les trames capteurs
# =============================================================================

from datetime import datetime
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# --- Configuration -----------------------------------------------------------

BROKER = "test.mosquitto.org"
PORT   = 1883

# Les deux topics à écouter
TOPICS = [
    "IUT/Colmar2026/SAE2.04/Maison1",
    "IUT/Colmar2026/SAE2.04/Maison2",
]

# --- Parsing -----------------------------------------------------------------

def parser_message(payload: str) -> dict | None:
    """
    Parse une trame du format :
      Id=12A6B8AF6CD3,piece=sejour,date=15/06/2026,heure=12:13:14,temp=26,35

    Version sans regex : on découpe sur les virgules, puis on recolle
    les deux derniers morceaux (partie entière et décimale de la température).
    """
    morceaux = payload.split(",")

    # On doit avoir 6 morceaux : Id, piece, date, heure, temp_entier, temp_decimal
    if len(morceaux) != 6:
        return None  # format non reconnu

    try:
        id_capteur = morceaux[0].split("=")[1]
        piece      = morceaux[1].split("=")[1]
        date       = morceaux[2].split("=")[1]
        heure      = morceaux[3].split("=")[1]

        # Les deux derniers morceaux sont la partie entière et décimale de temp
        temp_entier  = morceaux[4].split("=")[1]   # ex: "temp=26" -> "26"
        temp_decimal = morceaux[5]                  # ex: "35"

        temperature = float(f"{temp_entier}.{temp_decimal}")

    except (IndexError, ValueError):
        return None  # un champ attendu est manquant ou mal formé

    return {
        "id":          id_capteur,
        "piece":       piece,
        "date":        date,
        "heure":       heure,
        "temperature": temperature,
    }

# --- Callbacks MQTT ----------------------------------------------------------

def on_connect(client, userdata, connect_flags, reason_code, properties):
    """
    Callback appelé automatiquement à la fin de la tentative de connexion.
    reason_code == 0 signifie succès, toute autre valeur est une erreur.
    """
    if reason_code.is_failure:
        print(f"[ERREUR] Connexion refusée : {reason_code}")
        return

    print(f"[OK] Connecté au broker MQTT (code retour : {reason_code})")

    # On s'abonne à chaque topic une fois connecté
    for topic in TOPICS:
        client.subscribe(topic, qos=0)
        print(f"[OK] Abonné au topic : {topic}")

    print("\nEn attente de messages... (Ctrl+C pour arrêter)\n")
    print("-" * 60)


def on_message(client, userdata, message):
    """
    Callback appelé à chaque message reçu sur un topic abonné.
    """
    # Timestamp local de réception
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Décodage du payload binaire en chaîne UTF-8
    payload = message.payload.decode("utf-8")

    print(f"\n[{timestamp}] Message reçu sur : {message.topic}")

    donnees = parser_message(payload)
    if donnees:
        print(f"  ID capteur  : {donnees['id']}")
        print(f"  Pièce       : {donnees['piece']}")
        print(f"  Date        : {donnees['date']}")
        print(f"  Heure       : {donnees['heure']}")
        print(f"  Température : {donnees['temperature']:.2f} °C")
    else:
        # Affichage brut si le format ne correspond pas
        print(f"  [AVERTISSEMENT] Format non reconnu, message brut : {payload}")

# --- Programme principal -----------------------------------------------------

def main():
    # Création du client MQTT avec l'API version 2 (paho-mqtt >= 2.0)
    client = mqtt.Client(CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print(f"Connexion à {BROKER}:{PORT}...")
        client.connect(BROKER, PORT, keepalive=60)
        # loop_forever() bloque et traite les événements réseau en continu
        client.loop_forever()

    except KeyboardInterrupt:
        print("\nArrêt demandé par l'utilisateur.")
        client.disconnect()

    except Exception as erreur:
        print(f"[ERREUR] Impossible de joindre {BROKER} : {erreur}")


if __name__ == "__main__":
    main()
