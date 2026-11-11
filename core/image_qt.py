# SPDX-License-Identifier: GPL-3.0-or-later
"""Conversion d'une image Pillow vers un QPixmap."""

from io import BytesIO

from PIL import Image
from PyQt6.QtGui import QPixmap


def pil_vers_qpixmap(image: Image.Image) -> QPixmap:
    tampon = BytesIO()
    image.save(tampon, format="PNG")

    pixmap = QPixmap()
    pixmap.loadFromData(tampon.getvalue(), "PNG")
    return pixmap
