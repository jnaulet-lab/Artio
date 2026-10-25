# Configuration du Broker MQTT et Test de Liaison Home Assistant (Artio)

Ce document explique comment configurer le broker Mosquitto sous Home Assistant OS (HA OS) et exécuter un test de validation de la liaison MQTT entre le Raspberry Pi du robot **Artio** et Home Assistant.

---

## 01. Mise en place du broker MQTT sur HA OS

Avec HA OS, la configuration s'effectue via l'interface web. *(Note : Selon la version de Home Assistant, les modules complémentaires peuvent être nommés « Apps »)*.

1. **Installer et démarrer Mosquitto** :
   * Rendez-vous dans **Paramètres → Modules complémentaires** (ou **Apps**) **→ Boutique**.
   * Recherchez **Mosquitto broker** et installez-le.
   * Activez **Démarrer au boot** et **Watchdog**, puis cliquez sur **Démarrer**.
   * Une notification apparaît dans HA pour proposer l'intégration MQTT : cliquez sur **Configurer**, puis **Valider**. *(Si elle n'apparaît pas, allez dans Paramètres → Appareils et services → Ajouter une intégration → MQTT)*.

2. **Créer l'utilisateur MQTT pour le robot** :
   * Dans votre profil (icône en bas à gauche), activez le **Mode avancé** s'il n'est pas actif.
   * Allez dans **Paramètres → Personnes → onglet Utilisateurs → Ajouter un utilisateur**.
   * **Nom** : `artio`
   * Définissez un mot de passe solide (sans droits d'administration). Vous pouvez cocher l'option limitant la connexion au réseau local.
   * *Note : Mosquitto utilise la base d'utilisateurs d'HA. Ces identifiants serviront pour la connexion du robot.*
   * Réservez une adresse IP fixe pour le Pi hébergeant Home Assistant sur votre routeur/box.

---

## 02. Test de liaison sans servos : Capteur de température CPU dans HA

Ce test permet de vérifier la chaîne de communication `Pi Artio → Broker MQTT → Home Assistant` en créant un appareil virtuel **Artio** et une entité de télémétrie "Température CPU" via le mécanisme de découverte automatique MQTT (*MQTT Auto-Discovery*).

### A. Préparation sur le Pi du robot

Placez-vous dans le répertoire du projet et activez l'environnement virtuel :

```bash
cd ~/artio && source .venv/bin/activate
pip install paho-mqtt
```

Définissez vos variables d'environnement (remplacez par l'IP de votre serveur HA et vos identifiants) :

```bash
export MQTT_HOST="192.168.x.x"
export MQTT_USER="artio"
export MQTT_PASS="mot_de_passe"
```

### B. Script de test (`mqtt_test.py`)

Créez le script de test :

```python
# mqtt_test.py
import json
import os
import time
import paho.mqtt.client as mqtt

HOST = os.environ["MQTT_HOST"]
USER = os.environ["MQTT_USER"]
PASS = os.environ["MQTT_PASS"]

STATUS = "artio/status"
TEMP = "artio/telemetry/cpu_temp"
DISCOVERY = "homeassistant/sensor/artio/cpu_temp/config"

config = {
    "name": "Température CPU",
    "unique_id": "artio_cpu_temp",
    "state_topic": TEMP,
    "unit_of_measurement": "°C",
    "device_class": "temperature",
    "state_class": "measurement",
    "availability_topic": STATUS,
    "device": {
        "identifiers": ["artio"],
        "name": "Artio",
        "manufacturer": "DIY",
        "model": "Artio V1",
    },
}

def cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp") as f:
        return round(int(f.read()) / 1000, 1)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="artio_test_script")
client.username_pw_set(USER, PASS)
client.will_set(STATUS, "offline", retain=True)
client.connect(HOST, 1883)
client.loop_start()

# Publication du message de découverte HA et du statut de présence (Last Will)
client.publish(DISCOVERY, json.dumps(config), retain=True)
client.publish(STATUS, "online", retain=True)

try:
    while True:
        client.publish(TEMP, cpu_temp())
        time.sleep(10)
except KeyboardInterrupt:
    client.publish(STATUS, "offline", retain=True)
    client.loop_stop()
    client.disconnect()
```

Lancez le script :

```bash
python mqtt_test.py
```

### C. Validation dans Home Assistant

1. Dans Home Assistant, allez dans **Paramètres → Appareils et services → MQTT**.
2. L'appareil **Artio** doit apparaître automatiquement avec l'entité `sensor.artio_temperature_cpu` ("Température CPU").
3. Arrêtez le script avec `Ctrl+C` sur le Pi : l'entité doit passer à l'état **"Indisponible"** *(gestion du statut Last Will & Testament)*.

---

## 03. Diagnostic et dépannage

Si l'appareil n'apparaît pas ou si les données ne remontent pas :

* **Erreur d'authentification** : Le SDK MQTT peut échouer silencieusement lors d'une mauvaise authentification. Consultez l'onglet **Journal** du module Mosquitto dans HA pour vérifier s'il existe une ligne `not authorised`.
* **Connexion refusée** : Vérifiez que l'adresse IP du broker est correcte et que le service Mosquitto est bien démarré.
* **Écoute de sujets** : Dans HA (**Paramètres → Appareils et services → MQTT → Configurer**), écoutez le topic `artio/#` pour visualiser le flux de messages en direct.
* **Auto-Discovery** : Si les messages arrivent mais que l'appareil n'apparaît pas, assurez-vous que l'option de découverte automatique est activée dans la configuration de l'intégration MQTT.

---

## 04. Optimisation future (Base de données HA)

Afin d'éviter de surcharger la base de données de Home Assistant lors de la remontée d'un grand nombre de télémétries à haute fréquence (ex: positions/températures de 12 servomoteurs), il est recommandé d'exclure ces entités secondaires de l'enregistreur (*Recorder*) dans le fichier `configuration.yaml` de HA :

```yaml
recorder:
  exclude:
    entity_globs:
      - sensor.artio_servo_*
```
