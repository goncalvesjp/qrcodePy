"""Tests de la génération d'image QR code, avec et sans texte additionnel."""

from core.qr_generator import couleur_suffisamment_contrastee, generer_qr_image, generer_qr_pixmap


def test_sans_texte_additionnel():
    pixmap = generer_qr_pixmap("BEGIN:VCARD")
    assert not pixmap.isNull()


def test_avec_texte_au_dessus_et_en_dessous_agrandit_l_image():
    pixmap_seul = generer_qr_pixmap("BEGIN:VCARD")
    pixmap_avec_texte = generer_qr_pixmap(
        "BEGIN:VCARD", texte_haut="Jean Dupont", texte_bas="www.exemple.com"
    )

    assert not pixmap_avec_texte.isNull()
    assert pixmap_avec_texte.height() > pixmap_seul.height()


def test_texte_vide_ou_blanc_ne_change_pas_la_taille():
    pixmap_seul = generer_qr_pixmap("BEGIN:VCARD")
    pixmap_texte_blanc = generer_qr_pixmap("BEGIN:VCARD", texte_haut="   ", texte_bas="")

    assert pixmap_texte_blanc.height() == pixmap_seul.height()
    assert pixmap_texte_blanc.width() == pixmap_seul.width()


def test_avec_texte_accentue():
    pixmap = generer_qr_pixmap("BEGIN:VCARD", texte_haut="Société Générale Évènementiel")
    assert not pixmap.isNull()


def test_generer_qr_image_applique_la_couleur_choisie():
    image = generer_qr_image("BEGIN:VCARD", couleur="#0057B8")
    # Pixel dans le repère de coin (finder pattern, hors zone de silence) : doit porter la couleur choisie.
    assert image.getpixel((25, 25)) == (0, 87, 184)


def test_generer_qr_pixmap_avec_couleur():
    pixmap = generer_qr_pixmap("BEGIN:VCARD", couleur="#0057B8")
    assert not pixmap.isNull()


def test_couleur_suffisamment_contrastee():
    assert couleur_suffisamment_contrastee("#000000")
    assert couleur_suffisamment_contrastee("#0057B8")
    assert not couleur_suffisamment_contrastee("#FFFF00")
    assert not couleur_suffisamment_contrastee("#FFFFFF")
