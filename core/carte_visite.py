"""
Composition d'une carte de visite numérique : QR code + coordonnées
essentielles (nom, mobile, téléphone, email), au format carte de crédit
(ISO/CEI 7810 ID-1 : 85,6 × 54 mm) à 300 dpi, prête à imprimer ou à partager.
"""

from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtGui import QPixmap

from core.image_qt import pil_vers_qpixmap
from core.polices import charger_police
from core.qr_generator import generer_qr_image
from core.vcard import VCard

# Format ID-1 (carte de crédit / carte de visite standard) à 300 dpi.
_LARGEUR = 1011
_HAUTEUR = 638
_MARGE = 50
_ECART_QR_TEXTE = 40
_TAILLE_QR = 460  # borne haute : laisse assez de place au texte, QR encore très lisible

_COULEUR_FOND = (255, 255, 255)
_COULEUR_TEXTE = (24, 28, 44)
_COULEUR_SECONDAIRE = (110, 116, 130)


def generer_carte_pixmap(vcard: VCard, couleur_qr: str = "black") -> QPixmap:
    """Compose la carte de visite pour `vcard` et la retourne sous forme de QPixmap."""
    qr_image = generer_qr_image(vcard.to_vcard_string(), couleur_qr)
    return pil_vers_qpixmap(_composer_carte(vcard, qr_image))


def _composer_carte(vcard: VCard, qr_image: Image.Image) -> Image.Image:
    carte = Image.new("RGB", (_LARGEUR, _HAUTEUR), _COULEUR_FOND)
    dessin = ImageDraw.Draw(carte)

    taille_qr = min(_HAUTEUR - 2 * _MARGE, _TAILLE_QR)
    carte.paste(qr_image.resize((taille_qr, taille_qr)), (_MARGE, _MARGE))

    x_texte = _MARGE + taille_qr + _ECART_QR_TEXTE
    largeur_texte = _LARGEUR - x_texte - _MARGE

    police_label = charger_police(18)

    y = _MARGE

    nom_complet = " ".join(p for p in (vcard.prenom, vcard.nom) if p)
    if nom_complet:
        police, texte = _texte_ajuste(dessin, nom_complet, 44, 28, largeur_texte)
        dessin.text((x_texte, y), texte, font=police, fill=_COULEUR_TEXTE)
        y += 58

    sous_titre = " — ".join(p for p in (vcard.titre, vcard.societe) if p)
    if sous_titre:
        police, texte = _texte_ajuste(dessin, sous_titre, 26, 18, largeur_texte)
        dessin.text((x_texte, y), texte, font=police, fill=_COULEUR_SECONDAIRE)
        y += 42

    y += 24

    mobile = _premiere_valeur(vcard.mobiles_personnels, vcard.mobiles_professionnels)
    telephone = _premiere_valeur(vcard.telephones_travail, vcard.telephones_domicile)
    email = _premiere_valeur(vcard.emails)

    for label, valeur in (("Mobile", mobile), ("Téléphone", telephone), ("Email", email)):
        if not valeur:
            continue
        dessin.text((x_texte, y), label, font=police_label, fill=_COULEUR_SECONDAIRE)
        y += 26
        police, texte = _texte_ajuste(dessin, valeur, 28, 18, largeur_texte)
        dessin.text((x_texte, y), texte, font=police, fill=_COULEUR_TEXTE)
        y += 46

    return carte


def _premiere_valeur(*listes: list[str]) -> str:
    for liste in listes:
        if liste:
            return liste[0]
    return ""


def _texte_ajuste(
    dessin: ImageDraw.ImageDraw, texte: str, taille_max: int, taille_min: int, largeur_max: float
) -> tuple[ImageFont.ImageFont, str]:
    """Réduit la taille de police par paliers de 2px pour éviter de tronquer `texte`
    si possible ; ne tronque (avec une ellipse) qu'une fois `taille_min` atteinte."""
    for taille in range(taille_max, taille_min - 1, -2):
        police = charger_police(taille)
        if dessin.textlength(texte, font=police) <= largeur_max:
            return police, texte

    police = charger_police(taille_min)
    return police, _tronquer(dessin, texte, police, largeur_max)


def _tronquer(dessin: ImageDraw.ImageDraw, texte: str, police: ImageFont.ImageFont, largeur_max: float) -> str:
    """Raccourcit `texte` avec une ellipse s'il dépasse `largeur_max` à l'affichage."""
    if dessin.textlength(texte, font=police) <= largeur_max:
        return texte

    while texte and dessin.textlength(texte + "…", font=police) > largeur_max:
        texte = texte[:-1]
    texte = texte.rstrip(" —-")
    return texte + "…" if texte else "…"
