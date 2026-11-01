"""Tests de la composition de la carte de visite (QR code + coordonnées)."""

from core.carte_visite import _tronquer, generer_carte_pixmap
from core.polices import charger_police
from core.vcard import VCard
from PIL import Image, ImageDraw


def test_generer_carte_pixmap_taille_format_id1():
    vcard = VCard(prenom="Jean", nom="Dupont", emails=["jean@exemple.com"])
    pixmap = generer_carte_pixmap(vcard)

    assert not pixmap.isNull()
    assert pixmap.width() == 1011
    assert pixmap.height() == 638


def test_generer_carte_pixmap_avec_vcard_minimale():
    """Une vCard quasiment vide ne doit pas faire planter la composition."""
    pixmap = generer_carte_pixmap(VCard())
    assert not pixmap.isNull()


def test_generer_carte_pixmap_avec_couleur_personnalisee():
    vcard = VCard(prenom="Jean", nom="Dupont")
    pixmap = generer_carte_pixmap(vcard, couleur_qr="#0057B8")
    assert not pixmap.isNull()


def test_tronquer_laisse_le_texte_court_intact():
    dessin = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    police = charger_police(20)
    assert _tronquer(dessin, "Jean", police, 500) == "Jean"


def test_tronquer_raccourcit_le_texte_trop_long():
    dessin = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    police = charger_police(20)
    resultat = _tronquer(dessin, "jean.dupont@exemple-tres-long-domaine.com", police, 80)

    assert resultat.endswith("…")
    assert dessin.textlength(resultat, font=police) <= 80
