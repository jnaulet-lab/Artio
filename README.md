# Artio

**Plateforme de développement open source pour robots quadrupèdes imprimés en 3D, pilotés par Raspberry Pi, avec intégration domotique native (MQTT / Home Assistant).**

> ⚠️ **Statut : en développement actif (pré-alpha).** Le code fonctionne en simulation (bus de servos simulé). Les tests sur matériel réel sont en cours. L'API et la structure du dépôt peuvent évoluer.

---

## Objectifs

- Offrir une base **simple, lisible et hackable** pour construire un quadrupède 12 DOF (3 servos par patte).
- Fonctionner en **Python pur + MQTT**, sans dépendance obligatoire à ROS 2 (une passerelle ROS 2 pourra être ajoutée ultérieurement).
- Permettre de **développer sans robot** grâce à un bus de servomoteurs simulé.
- Faire du robot un **objet de la maison connectée** : télémétrie, commandes et automatisations via Home Assistant.

---

## Filiation et crédits

Artio s'inscrit dans la lignée de plusieurs projets de quadrupèdes open source et en fusionne l'esprit :

- **SpotMicro** : le projet d'origine conçu par Deok-yeon Kim.
- **NovaSM3** ([novaspotmicro.com](https://novaspotmicro.com/)) : la suite conçue par Chris Locke, dont la structure centrale « Bones & Covers » sert de base.
- **jAQ** ([github.com/MatthiasWM/JaQ](https://github.com/MatthiasWM/JaQ)) : une variante modernisée par MatthiasWM permettant l'intégration native des servomoteurs Feetech STS3215 dans la mécanique des pattes.

> Artio est un projet **indépendant** : il n'est ni affilié à ces projets ni une version officielle de l'un d'eux. Les modèles 3D, plans et documents de ces projets restent soumis à **leurs propres licences**, auxquelles il convient de se reporter.

---

## Architecture

### Matériel (référence)

| Composant | Choix de référence |
|---|---|
| **Structure** | Base NovaSM3 (« Bones & Covers ») + Pattes jAQ imprimées en 3D (PETG/ABS, embouts en TPU) |
| **Cerveau** | Raspberry Pi 4 (4 Go), Raspberry Pi OS Lite 64 bits |
| **Servomoteurs** | 12 × Feetech STS3215 / STS3217 (bus série TTL, 1 Mbps) |
| **Alimentation** | LiPo 2S/3S, lignes d'alimentation séparées (UBEC 5V pour le Pi), masse commune |
| **Interfaces (optionnel)** | M5Stack CoreS3, télécommande M5Cardputer / M5StickC (ESP-NOW) |
| **Capteurs de sol (optionnel)** | Microswitches ou capteurs FSR intégrés aux pieds |

### Logiciel

```text
          ┌──────────────────────────────┐
          │        Home Assistant        │
          └──────────────┬───────────────┘
                         │ MQTT
          ┌──────────────┴───────────────┐
          │   Artio (Python, Raspberry)  │
          │  ┌────────────────────────┐  │
          │  │ Contrôleur / Marche    │  │
          │  ├────────────────────────┤  │
          │  │ Cinématique Inverse    │  │
          │  ├────────────────────────┤  │
          │  │ ServoBus (interface)   │  │
          │  └───────┬────────┬───────┘  │
          └──────────┼────────┼──────────┘
              Feetech (réel)  SimServoBus (simulation)
```

Le bus de servomoteurs est abstrait derrière l'interface `ServoBus`, permettant de basculer entre l'exécution sur le matériel réel (`FeetechServoBus`) et une boucle virtuelle (`SimServoBus`).

## État d'avancement

- [x] Interface `ServoBus` et bus simulé (`SimServoBus`)
- [x] Cinématique inverse d'une patte
- [x] Contrôleur et entités Home Assistant (avec faux bus de servos)
- [x] Liaison MQTT avec Home Assistant
- [ ] Tests sur servos réels (Feetech STS)
- [ ] Cinématique des quatre pattes et posture statique
- [ ] Génération de marche
- [ ] Capteurs de contact au sol
- [ ] Documentation de montage et de calibration

## Démarrage rapide (simulation, sans robot)

```bash
# Clone du dépôt public
git clone git@github.com:jnaulet-lab/artio.git
cd artio

# Création et activation de l'environnement virtuel Python
python3 -m venv .venv
source .venv/bin/activate

# Installation du package en mode éditable
pip install -e .

# Préparation de la configuration locale
cp config.example.yaml config.yaml
# Éditez config.yaml avec les accès de votre broker MQTT (laisser simulate: true)
```

## Structure du dépôt

```
artio/
├── src/artio/             # Package Python principal (bus, cinématique, contrôleur, MQTT)
├── hardware/              # Fichiers CAO (STEP/FreeCAD), STL imprimables, schémas, BOM
├── docs/                  # Guides d'assemblage, câblage, calibration et API MQTT
├── config.example.yaml    # Modèle de configuration générique (exemples de topics/broker)
└── tests/                 # Tests unitaires du moteur cinématique et du bus
```

> **Sécurité & Confidentialité** : Le fichier de configuration réel (`config.yaml`), contenant vos identifiants MQTT, tokens et adresses IP, est exclu du suivi Git via le .gitignore. Seul `config.example.yaml` est versionné.

## Contribuer

Les suggestions, signalements de bugs (issues) et propositions de modifications (pull requests) sont vivement encouragés. Le projet évoluant rapidement, privilégiez l'ouverture d'une issue pour échanger sur une fonctionnalité importante avant de soumettre du code.

## Licence

Ce projet est distribué sous licence MIT.
