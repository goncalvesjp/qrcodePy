# SPDX-License-Identifier: GPL-3.0-or-later
"""Enregistrement d'une image (QR code, carte de visite, ...) sur disque (PNG, JPEG ou PDF)."""

from PyQt6.QtCore import QMarginsF, QSizeF
from PyQt6.QtGui import QPageSize, QPainter, QPdfWriter, QPixmap

FILTRES = "Image PNG (*.png);;Image JPEG (*.jpg *.jpeg);;Document PDF (*.pdf)"

_EXTENSIONS_PAR_FILTRE = {
    "Image PNG (*.png)": (".png",),
    "Image JPEG (*.jpg *.jpeg)": (".jpg", ".jpeg"),
    "Document PDF (*.pdf)": (".pdf",),
}


def completer_extension(chemin: str, filtre: str) -> str:
    """Ajoute l'extension par défaut du filtre choisi si le chemin n'en a pas déjà une adaptée."""
    extensions = _EXTENSIONS_PAR_FILTRE.get(filtre)
    if not extensions or chemin.lower().endswith(extensions):
        return chemin
    return chemin + extensions[0]


def enregistrer_image(pixmap: QPixmap, chemin: str) -> None:
    """Enregistre `pixmap` en PNG, JPEG ou PDF selon l'extension de `chemin`."""
    extension = chemin.rsplit(".", 1)[-1].lower() if "." in chemin else ""

    if extension == "pdf":
        _enregistrer_en_pdf(pixmap, chemin)
    elif extension in ("jpg", "jpeg"):
        if not pixmap.save(chemin, "JPEG"):
            raise OSError(f"Impossible d'enregistrer l'image JPEG : {chemin}")
    else:
        if not pixmap.save(chemin, "PNG"):
            raise OSError(f"Impossible d'enregistrer l'image PNG : {chemin}")


def _enregistrer_en_pdf(pixmap: QPixmap, chemin: str) -> None:
    """Place l'image, à sa taille d'origine en pixels, sur une page PDF à sa mesure."""
    resolution = 300  # points par pouce, détermine la taille physique de la page

    writer = QPdfWriter(chemin)
    writer.setResolution(resolution)
    taille_page_points = QSizeF(
        pixmap.width() / resolution * 72,
        pixmap.height() / resolution * 72,
    )
    writer.setPageSize(QPageSize(taille_page_points, QPageSize.Unit.Point))
    writer.setPageMargins(QMarginsF(0, 0, 0, 0))

    painter = QPainter()
    if not painter.begin(writer):
        raise OSError(f"Impossible d'enregistrer le PDF : {chemin}")
    painter.drawPixmap(0, 0, pixmap)
    painter.end()
