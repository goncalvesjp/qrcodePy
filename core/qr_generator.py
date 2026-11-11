# SPDX-License-Identifier: GPL-3.0-or-later
"""Génération d'images de QR code, avec texte optionnel au-dessus/en-dessous."""

import qrcode
from PIL import Image, ImageColor, ImageDraw, ImageFont
from PyQt6.QtGui import QPixmap

from core.image_qt import pil_vers_qpixmap
from core.polices import charger_police

_MARGE = 10


def couleur_suffisamment_contrastee(couleur: str, seuil: float = 0.6) -> bool:
    """Indique si `couleur` est assez sombre pour rester scannable sur fond blanc.

    Les lecteurs de QR code ont besoin d'un fort contraste entre modules et fond ;
    une couleur trop claire (luminance relative élevée) rend le code peu fiable."""
    r, g, b = ImageColor.getrgb(couleur)
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    return luminance <= seuil


def generer_qr_image(donnees: str, couleur: str = "black") -> Image.Image:
    """Encode `donnees` dans un QR code et retourne l'image Pillow correspondante (sans texte).
    `couleur` est la couleur des modules (ex: '#000000'), sur fond blanc."""
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2)
    qr.add_data(donnees)
    qr.make(fit=True)
    return qr.make_image(fill_color=couleur, back_color="white").convert("RGB")


def generer_qr_pixmap(donnees: str, texte_haut: str = "", texte_bas: str = "", couleur: str = "black") -> QPixmap:
    """Encode `donnees` dans un QR code, avec un texte optionnel au-dessus
    et/ou en-dessous, et retourne le résultat sous forme de QPixmap."""
    qr_image = generer_qr_image(donnees, couleur)
    image_finale = _ajouter_textes(qr_image, texte_haut.strip(), texte_bas.strip())
    return pil_vers_qpixmap(image_finale)


def _ajouter_textes(qr_image: Image.Image, texte_haut: str, texte_bas: str) -> Image.Image:
    """Compose le QR code avec un bandeau de texte au-dessus et/ou en-dessous."""
    if not texte_haut and not texte_bas:
        return qr_image

    police = charger_police(max(16, qr_image.width // 18))
    dessin_mesure = ImageDraw.Draw(qr_image)

    largeur_haut, hauteur_haut = _dimensions_texte(dessin_mesure, texte_haut, police)
    largeur_bas, hauteur_bas = _dimensions_texte(dessin_mesure, texte_bas, police)

    bande_haut = hauteur_haut + 2 * _MARGE if texte_haut else 0
    bande_bas = hauteur_bas + 2 * _MARGE if texte_bas else 0
    largeur = max(qr_image.width, largeur_haut, largeur_bas) + 2 * _MARGE
    hauteur = bande_haut + qr_image.height + bande_bas

    image_finale = Image.new("RGB", (largeur, hauteur), "white")
    dessin = ImageDraw.Draw(image_finale)

    if texte_haut:
        dessin.text(((largeur - largeur_haut) / 2, _MARGE), texte_haut, fill="black", font=police)

    image_finale.paste(qr_image, ((largeur - qr_image.width) // 2, bande_haut))

    if texte_bas:
        y_bas = bande_haut + qr_image.height + _MARGE
        dessin.text(((largeur - largeur_bas) / 2, y_bas), texte_bas, fill="black", font=police)

    return image_finale


def _dimensions_texte(dessin: ImageDraw.ImageDraw, texte: str, police: ImageFont.ImageFont) -> tuple[int, int]:
    if not texte:
        return 0, 0
    gauche, haut, droite, bas = dessin.textbbox((0, 0), texte, font=police)
    return droite - gauche, bas - haut
