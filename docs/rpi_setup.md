# Procédure d'installation et de configuration : Raspberry Pi 4 (Artio)

Ce guide détaille la procédure d'installation et de configuration de base du Raspberry Pi 4 (4 Go) sous **Raspberry Pi OS Lite 64 bits** pour la plateforme robotique **Artio**.

---

## 00. Matériel requis
- **Raspberry Pi 4 (4 Go)**.
- **Carte microSD** de 32 Go ou plus (A2, idéalement *High Endurance*).
- **Alimentation** 5 V / 3 A (ou UBEC 5 V dédié).
- Dissipateur thermique ou ventilateur.
- Un PC pour préparer la carte microSD.
- Un adaptateur USB-Série (carte de debug Feetech FE-URT-1 ou équivalent Waveshare).
- Servomoteurs Feetech STS3215 / STS3217 et une alimentation externe dédiée.
- *(Optionnel)* Un bouton-poussoir pour l'arrêt propre du système.

---

## 01. Préparation de la carte MicroSD

1. Téléchargez et ouvrez **Raspberry Pi Imager** sur votre ordinateur.
2. Choisissez le système d'exploitation : **Raspberry Pi OS (other) → Raspberry Pi OS Lite (64-bit)**.
3. Sélectionnez votre carte MicroSD.
4. Cliquez sur l'icône d'engrenage / personnalisation (*OS Customization*) :
   - **Nom d'hôte (Hostname)** : `artio` (ou `artio.local`)
   - **Utilisateur et mot de passe** : Définissez votre identifiant (ex: `artio`)
   - **Clé SSH** ou activation SSH par mot de passe
   - **Réseau Wi-Fi** : Renseignez votre SSID et mot de passe
   - **Fuseau horaire** : `Europe/Paris`
   - **Disposition du clavier** : `fr`
5. Lancez l'écriture sur la carte. Une fois terminée, insérez la carte dans le Pi et branchez l'alimentation.

---

## 02. Premier démarrage et mise à jour

1. Connectez-vous au Raspberry Pi via SSH depuis votre terminal PC :

```bash
ssh <utilisateur>@artio.local
```

2. Mettez à jour l'ensemble du système :

```bash
sudo apt update && sudo apt full-upgrade -y
```

3. Redémarrez le Raspberry Pi :

```bash
sudo reboot
```

---

## 03. Réglages système et interfaces

1. Connectez-vous à nouveau en SSH (`ssh <utilisateur>@artio.local`).
2. Éditez le fichier `/boot/firmware/config.txt` :

```bash
sudo nano /boot/firmware/config.txt
```

Ajoutez les lignes suivantes à la fin du fichier *(remarque : si `dtparam=i2c_arm=on` existe déjà en commentaire, décommentez-la au lieu de la dupliquer)* :

```ini
dtparam=i2c_arm=on
dtparam=i2c_arm_baudrate=400000
dtoverlay=gpio-shutdown,gpio_pin=17
```

> **Note sur le GPIO shutdown (optionnel)** : Un bouton entre le GPIO 17 et la masse déclenchera un arrêt propre du Pi. On évite le GPIO 3 (broche par défaut de cet overlay) car il est réservé à la ligne SCL de l'I2C.

3. Installez les outils système nécessaires et ajoutez votre utilisateur aux groupes d'accès matériel :

```bash
sudo apt install -y i2c-tools git htop python3-venv python3-pip python3-numpy python3-opencv
sudo usermod -aG i2c,dialout,gpio $USER
```

4. Redémarrez pour appliquer les permissions et la configuration d'overlay :

```bash
sudo reboot
```

---

## 04. Optimisation de la mémoire (RAM et carte SD)

### A. Gestion du Swap (ZRAM)
Vérifiez d'abord la configuration actuelle :

```bash
swapon --show
free -h
```

- Si un swap de type **zram** est déjà présent, aucune action n'est requise.
- Si le swap utilise un fichier physique sur la carte SD (`dphys-swapfile`), remplacez-le par **zram** afin de préserver la durée de vie de la carte SD :

```bash
sudo systemctl disable --now dphys-swapfile
sudo apt install -y zram-tools
```

Éditez la configuration zram :

```bash
sudo nano /etc/default/zramswap
```
*(Définissez `PERCENT=50` et `ALGO=zstd`)*

Relancez le service :

```bash
sudo systemctl restart zramswap
```

### B. Restriction de la taille des journaux
Afin d'éviter de saturer le stockage :

```bash
sudo nano /etc/systemd/journald.conf
```
*(Définissez ou décommentez `SystemMaxUse=100M`)*

Appliquez le changement :

```bash
sudo systemctl restart systemd-journald
```

### C. Options de montage (`noatime`)
Vérifiez votre fichier `/etc/fstab` (`cat /etc/fstab`). L'option `noatime` est généralement déjà activée par défaut sur la partition racine sous Raspberry Pi OS Lite.

---

## 05. Configuration réseau

- **Adresse IP fixe** : Il est recommandé de réserver une adresse IP statique pour le Pi directement depuis l'interface de votre routeur/box internet.
- **Gestion de l'énergie Wi-Fi** : Si vous constatez des déconnexions intempestives en Wi-Fi, désactivez la mise en veille de la carte sans fil :

```bash
# Affiche le nom de votre connexion
nmcli connection show

# Désactive l'économie d'énergie (remplacez <nom> par le nom de votre connexion)
sudo nmcli connection modify "<nom>" 802-11-wireless.powersave 2
sudo nmcli connection up "<nom>"
```

---

## 06. Environnement virtuel Python et dépendances Artio

1. Créez le répertoire du projet **Artio**, initialisez le dépôt Git et préparez l'environnement Python :

```bash
mkdir -p ~/artio && cd ~/artio
git init
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
```

2. Installez les paquets de base dans l'environnement virtuel :

```bash
pip install pyserial feetech-servo-sdk paho-mqtt
```

> **Note** : Le paquet `feetech-servo-sdk` fournit le module `scservo_sdk` nécessaire au contrôle des servos STS. Veillez à toujours travailler avec l'environnement virtuel activé (`source .venv/bin/activate`).
