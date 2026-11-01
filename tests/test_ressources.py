"""Tests de la résolution de chemins de ressources."""

import re

from core.ressources import RACINE_PROJET, chemin_ressource, version_application


def test_chemin_ressource_pointe_vers_l_icone_existante():
    chemin = chemin_ressource("assets/icon.png")
    assert chemin.exists()


def test_racine_projet_contient_main_py():
    assert (RACINE_PROJET / "main.py").exists()


def test_version_application_suit_le_format_semver():
    assert re.fullmatch(r"\d+\.\d+\.\d+", version_application())
