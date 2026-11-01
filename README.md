# QR Visite

Application de bureau PyQt6 pour générer des QR codes. Premier type pris en
charge : carte de contact (vCard), avec nom, prénom, société, email(s),
mobile(s), téléphone(s) et adresse.

En plus du QR code seul, l'application peut générer une **carte de visite
numérique** (`core/carte_visite.py`) : QR code + nom, mobile, téléphone et
email au format carte de crédit (ISO/CEI 7810 ID-1), exportable en PNG, JPEG
ou PDF — à enregistrer, imprimer ou partager (ce n'est pas un pass Apple
Wallet/Cartes à proprement parler : cela nécessiterait un certificat Apple
Developer "Pass Type ID" pour signer un fichier `.pkpass`).

## Prérequis

- Python 3
- PyQt6 (installé via `requirements.txt`)

## Installation

```bash
make venv
```

Équivalent manuel :

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Lancer l'application

```bash
make run
```

## Tests

```bash
make test
```

Lance la suite `pytest` (`tests/`) en mode Qt "offscreen" (aucune fenêtre
n'apparaît pendant les tests).

## Packaging (exécutables autonomes)

### macOS

```bash
make macos
```

Produit `dist/macos/QRVisite.app` via [PyInstaller](https://pyinstaller.org/).

### Linux

```bash
make linux
```

Produit `dist/linux/qr-visite` (binaire ELF x86_64 autonome).

Ce build est fait dans un conteneur Ubuntu via
[`container`](https://github.com/apple/container), l'outil de
conteneurisation natif d'Apple (macOS 15+, Apple Silicon). Le conteneur
cible `amd64` (via Rosetta) car PyQt6 ne fournit pas de wheel Linux arm64
précompilée sur PyPI.

Le binaire produit dépend de quelques bibliothèques système Qt/X11
généralement déjà présentes sur un bureau Linux (`libgl1`, `libegl1`,
`libglib2.0-0`, la pile `libxcb-*`, `libdbus-1-3`, `libfontconfig1`) ; sur un
système minimal, les installer via le gestionnaire de paquets si l'exécutable
ne démarre pas.

Le texte dessiné au-dessus/en-dessous du QR code (voir `core/qr_generator.py`)
cherche une police système (DejaVu Sans puis Liberation Sans) pour afficher
correctement les caractères accentués ; sur un système minimal sans aucune de
ces polices, installer `fonts-dejavu-core` (ou équivalent) si les accents
s'affichent mal.

### Nettoyer les artefacts de build

```bash
make clean
```

## Structure du projet

```
main.py                  Point d'entrée
core/                     Logique métier de l'application
gui/                      Fichiers .py générés depuis ui/*.ui via pyuic6
ui/                       Fichiers source Qt Designer (.ui)
assets/                   Icône de l'application (icon.png, icon.icns)
tests/                    Suite de tests pytest
packaging/                Specs PyInstaller (macOS, Linux) et Dockerfile de build Linux
```

Pour changer l'icône : remplacer `assets/icon.png` (idéalement 1024×1024) puis
régénérer `assets/icon.icns` pour macOS, par exemple avec `sips`/`iconutil` :

```bash
mkdir /tmp/AppIcon.iconset
for taille in 16 32 128 256 512; do
  sips -z $taille $taille assets/icon.png --out /tmp/AppIcon.iconset/icon_${taille}x${taille}.png
  sips -z $((taille*2)) $((taille*2)) assets/icon.png --out /tmp/AppIcon.iconset/icon_${taille}x${taille}@2x.png
done
iconutil -c icns /tmp/AppIcon.iconset -o assets/icon.icns
```

Pour modifier l'interface : éditer les fichiers `.ui` avec Qt Designer, puis
régénérer les fichiers `gui/ui_*.py` correspondants avec :

```bash
make ui
```

## Ajouter un nouveau type de QR code

- `core/vcard.py` : modèle de données + sérialisation vCard. Pour un nouveau
  type (URL, Wi-Fi, texte libre, ...), ajouter un module similaire exposant
  une méthode `to_...` qui retourne la chaîne à encoder.
- `core/qr_generator.py` : génère l'image à partir d'une chaîne quelconque
  (indépendant du type de contenu).
- `core/main_window.py` : relie le formulaire (`ui/main_window.ui`) aux
  modules ci-dessus. Pour plusieurs types de QR code, envisager un
  `QTabWidget`/`QStackedWidget` avec un formulaire par type.
