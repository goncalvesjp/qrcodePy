"""Génération d'images de QR code, avec texte optionnel au-dessus/en-dessous."""

import sys
from io import BytesIO
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtGui import QPixmap

_MARGE = 10

# La police par défaut de Pillow (ImageFont.load_default) ne couvre pas les
# caractères accentués du français : on préfère une police système courante,
# en repli uniquement si aucune n'est disponible.
_POLICES_SYSTEME = {
    "darwin": [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ],
    "linux": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ],
    "win32": [
        "C:\\Windows\\Fonts\\arial.ttf",
    ],
}


def _charger_police(taille: int) -> ImageFont.ImageFont:
    """Charge une police système supportant les accents ; repli sur la police
    par défaut de Pillow si aucune police système n'est trouvée."""
    for chemin in _POLICES_SYSTEME.get(sys.platform, []):
        if Path(chemin).exists():
            try:
                return ImageFont.truetype(chemin, size=taille)
            except OSError:
                continue
    return ImageFont.load_default(size=taille)


def generer_qr_pixmap(donnees: str, texte_haut: str = "", texte_bas: str = "") -> QPixmap:
    """Encode `donnees` dans un QR code, avec un texte optionnel au-dessus
    et/ou en-dessous, et retourne le résultat sous forme de QPixmap."""
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2)
    qr.add_data(donnees)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    image_finale = _ajouter_textes(qr_image, texte_haut.strip(), texte_bas.strip())

    tampon = BytesIO()
    image_finale.save(tampon, format="PNG")

    pixmap = QPixmap()
    pixmap.loadFromData(tampon.getvalue(), "PNG")
    return pixmap


def _ajouter_textes(qr_image: Image.Image, texte_haut: str, texte_bas: str) -> Image.Image:
    """Compose le QR code avec un bandeau de texte au-dessus et/ou en-dessous."""
    if not texte_haut and not texte_bas:
        return qr_image

    police = _charger_police(max(16, qr_image.width // 18))
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
