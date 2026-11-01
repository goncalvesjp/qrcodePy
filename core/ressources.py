"""
Résolution de chemins vers les ressources embarquées (icône, ...).

Fonctionne aussi bien en lançant l'application depuis les sources qu'une
fois empaquetée avec PyInstaller (qui extrait les fichiers déclarés dans
`datas` sous un dossier temporaire désigné par `sys._MEIPASS`).
"""

import sys
from pathlib import Path

RACINE_PROJET = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))


def chemin_ressource(chemin_relatif: str) -> Path:
    """Retourne le chemin absolu d'une ressource (ex: `chemin_ressource("assets/icon.png")`)."""
    return RACINE_PROJET / chemin_relatif


def version_application() -> str:
    """Lit le numéro de version depuis le fichier VERSION à la racine du projet."""
    return chemin_ressource("VERSION").read_text(encoding="utf-8").strip()
