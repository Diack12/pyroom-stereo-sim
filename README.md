# 🎧 Création d’Effets Sonores Stéréo Dynamiques pour la Vidéoconférence Basés sur la Détection de Visage

## 🔍 Objectif du Projet

Ce projet vise à recréer une expérience sonore plus immersive et naturelle lors de visioconférences. Pour cela, il applique des **effets stéréo dynamiques** à la voix de l’orateur, en fonction de sa **position détectée par la webcam**.

L’idée principale est de simuler la perception du son comme si l’orateur se déplaçait dans une pièce, en combinant :

* 📷 **Détection de visage** en temps réel
* 🎧 **Spatialisation stéréo dynamique**
* 🔺 **Simulation acoustique avec PyroomAcoustics**
* 🔍 **Vue 2D temps réel** de la scène simulée

---

## 🚀 Fonctionnalités principales

* 👤 Détection automatique du visage de l'orateur avec `cvlib`
* 🔴 Simulation d'une pièce avec `pyroomacoustics` (mur, absorption, réverbération)
* 🔀 Spatialisation stéréo : 1 canal ou 2 canaux selon le fichier utilisé
* 📊 Affichage 2D en temps réel : caméra + position dans la salle

---

## 🌐 Technologies utilisées

* Python 3.10+
* OpenCV
* PyRoomAcoustics
* Sounddevice
* cvlib
* numpy

---

## 📁 Fichiers principaux

| Nom du fichier                     | Description                                                     |
| ---------------------------------- | --------------------------------------------------------------- |
| `SimulationStereo_TempsReel.py`    | Version mono (1 canal audio), détection visage + spatialisation |
| `SimulationStereo_TempsReel_v2.py` | Version stéréo (2 canaux audio), spatialisation gauche/droite   |

Tous les autres fichiers ne sont pas utilisés dans la version finale.

---

## 🛠️ Installation

1. Cloner ce dépôt GitHub :

```bash
git clone https://github.com/Diack12/pyroom-stereo-sim.git
cd pyroom-stereo-sim
```

2. Installer les dépendances (de préférence dans un venv) :

```bash
pip install -r requirements.txt
```



3. Lancer un des deux scripts :

```bash
python SimulationStereo_TempsReel_v2.py   # version stéréo
# ou
python SimulationStereo_TempsReel.py       # version mono
```

---

## 🚮 Limitations

* La réverbération est précalculée avec un coefficient fixe d’absorption
* La détection de visage n’est pas toujours robuste
* Latence potentielle dû au blocksize audio ou au traitement

---

## 💼 Auteurs / Crédits

Projet réalisé dans le cadre d'un travail d'équipe :
\- Papa Djidiack Faye
\- Papa Oumar Fall
\- Yassine Yahiaoui
\- Mahamadou Coulibaly

---

## 💡 Idées d'amélioration

* Enregistrement de la vidéo avec audio spatial
* Ajout de bruit ambiant pour plus de réalisme
* Amélioration de la détection de tête avec `mediapipe`
* Calcul des RIRs en GPU pour réduire la latence
