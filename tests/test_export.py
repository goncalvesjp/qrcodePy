"""Tests de l'enregistrement d'une image en PNG, JPEG et PDF."""

from core.export import completer_extension, enregistrer_image
from core.qr_generator import generer_qr_pixmap


def test_completer_extension_ajoute_le_suffixe_manquant():
    assert completer_extension("qrcode", "Image PNG (*.png)") == "qrcode.png"
    assert completer_extension("qrcode", "Image JPEG (*.jpg *.jpeg)") == "qrcode.jpg"
    assert completer_extension("qrcode", "Document PDF (*.pdf)") == "qrcode.pdf"


def test_completer_extension_ne_duplique_pas_le_suffixe_existant():
    assert completer_extension("qrcode.png", "Image PNG (*.png)") == "qrcode.png"
    assert completer_extension("qrcode.jpeg", "Image JPEG (*.jpg *.jpeg)") == "qrcode.jpeg"


def test_enregistrer_image_png(tmp_path):
    pixmap = generer_qr_pixmap("BEGIN:VCARD")
    chemin = tmp_path / "qrcode.png"

    enregistrer_image(pixmap, str(chemin))

    assert chemin.exists()
    assert chemin.read_bytes().startswith(b"\x89PNG")


def test_enregistrer_image_jpeg(tmp_path):
    pixmap = generer_qr_pixmap("BEGIN:VCARD")
    chemin = tmp_path / "qrcode.jpg"

    enregistrer_image(pixmap, str(chemin))

    assert chemin.exists()
    assert chemin.read_bytes().startswith(b"\xff\xd8")


def test_enregistrer_image_pdf(tmp_path):
    pixmap = generer_qr_pixmap("BEGIN:VCARD")
    chemin = tmp_path / "qrcode.pdf"

    enregistrer_image(pixmap, str(chemin))

    assert chemin.exists()
    assert chemin.read_bytes().startswith(b"%PDF")
