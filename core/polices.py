# SPDX-License-Identifier: GPL-3.0-or-later
"""Chargement de police pour le texte dessiné sur les images générées (QR code, carte)."""

import sys
from pathlib import Path

from PIL import ImageFont

# La police par défaut de Pillow (ImageFont.load_default) ne couvre pas les
# caractères accentués du français : on préfère une police système courante,
# en repli uniquement si aucune n'est disponible.
POLICES_SYSTEME = {
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


def charger_police(taille: int) -> ImageFont.ImageFont:
    """Charge une police système supportant les accents ; repli sur la police
    par défaut de Pillow si aucune police système n'est trouvée."""
    for chemin in POLICES_SYSTEME.get(sys.platform, []):
        if Path(chemin).exists():
            try:
                return ImageFont.truetype(chemin, size=taille)
            except OSError:
                continue
    return ImageFont.load_default(size=taille)
