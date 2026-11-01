"""Tests du chargement de police (support des accents français)."""

from core.polices import charger_police


def test_police_supporte_les_caracteres_accentues_francais():
    """La police utilisée doit avoir un glyphe (de l'encre) pour les lettres accentuées,
    contrairement à la police par défaut de Pillow qui ne les couvre pas."""
    police = charger_police(24)
    for caractere in "éèàçùô":
        assert police.getmask(caractere).getbbox() is not None
