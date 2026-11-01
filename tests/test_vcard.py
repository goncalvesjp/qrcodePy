"""Tests de la construction de la chaîne vCard."""

from core.vcard import VCard


def test_depuis_champs_decoupe_les_valeurs_multiples():
    vcard = VCard.depuis_champs(
        prenom="Jean",
        nom="Dupont",
        societe="Acme",
        titre="Directeur commercial",
        emails="jean@exemple.com; j.dupont@travail.com",
        mobiles_personnels="0612345678",
        mobiles_professionnels="",
        mobile_secondaire="  0611112222  ",
        telephones_domicile="",
        telephones_travail="0123456789; 0198765432",
        telephones_fax="",
        adresse="1 rue de la Paix, 75002 Paris",
        url="www.exemple.com",
        linkedin="jean-dupont",
        note="Contact préféré",
    )

    assert vcard.emails == ["jean@exemple.com", "j.dupont@travail.com"]
    assert vcard.mobiles_personnels == ["0612345678"]
    assert vcard.mobiles_professionnels == []
    assert vcard.mobile_secondaire == "0611112222"
    assert vcard.telephones_domicile == []
    assert vcard.telephones_travail == ["0123456789", "0198765432"]
    assert vcard.url == "https://www.exemple.com"
    assert vcard.linkedin == "https://www.linkedin.com/in/jean-dupont"


def test_normalisation_url_et_linkedin_deja_complets():
    vcard = VCard.depuis_champs(
        prenom="",
        nom="",
        societe="",
        titre="",
        emails="",
        mobiles_personnels="",
        mobiles_professionnels="",
        mobile_secondaire="",
        telephones_domicile="",
        telephones_travail="",
        telephones_fax="",
        adresse="",
        url="https://exemple.com",
        linkedin="https://www.linkedin.com/in/jean-dupont",
        note="",
    )

    assert vcard.url == "https://exemple.com"
    assert vcard.linkedin == "https://www.linkedin.com/in/jean-dupont"


def test_to_vcard_string_contient_les_champs_attendus():
    vcard = VCard(
        prenom="Jean",
        nom="Dupont",
        societe="Acme",
        titre="Directeur commercial",
        emails=["jean@exemple.com"],
        mobiles_personnels=["0612345678"],
        mobiles_professionnels=["0700000000"],
        mobile_secondaire="0611112222",
        telephones_domicile=["0123456789"],
        telephones_travail=["0198765432"],
        telephones_fax=["0111111111"],
        adresse="1 rue de la Paix, 75002 Paris",
        url="https://www.exemple.com",
        linkedin="https://www.linkedin.com/in/jean-dupont",
        note="Contact préféré",
    )

    texte = vcard.to_vcard_string()

    assert texte.startswith("BEGIN:VCARD\r\nVERSION:3.0\r\n")
    assert texte.endswith("END:VCARD\r\n")
    assert "N:Dupont;Jean;;;" in texte
    assert "FN:Jean Dupont" in texte
    assert "ORG:Acme" in texte
    assert "TITLE:Directeur commercial" in texte
    assert "TEL;TYPE=CELL,HOME:0612345678" in texte
    assert "TEL;TYPE=CELL,WORK:0700000000" in texte
    assert "TEL;TYPE=CELL:0611112222" in texte
    assert "TEL;TYPE=HOME,VOICE:0123456789" in texte
    assert "TEL;TYPE=WORK,VOICE:0198765432" in texte
    assert "TEL;TYPE=FAX:0111111111" in texte
    assert "EMAIL;TYPE=INTERNET:jean@exemple.com" in texte
    assert "ADR;TYPE=HOME:;;1 rue de la Paix\\, 75002 Paris;;;;" in texte
    assert "URL:https://www.exemple.com" in texte
    assert "X-SOCIALPROFILE;TYPE=linkedin:https://www.linkedin.com/in/jean-dupont" in texte
    assert "NOTE:Contact préféré" in texte


def test_est_vide():
    assert VCard().est_vide()
    assert not VCard(prenom="Jean").est_vide()
    assert not VCard(linkedin="https://www.linkedin.com/in/jean-dupont").est_vide()
    assert not VCard(mobile_secondaire="0611112222").est_vide()
