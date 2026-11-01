"""
Construction de la charge utile vCard (RFC 2426, version 3.0) pour un QR code
de type carte de contact.
"""

from dataclasses import dataclass, field


def _escape(valeur: str) -> str:
    """Échappe les caractères spéciaux d'un champ vCard (backslash, virgule,
    point-virgule, retour à la ligne)."""
    return (
        valeur.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
    )


def _valeurs_multiples(texte: str) -> list[str]:
    """Découpe un champ saisi par l'utilisateur en plusieurs valeurs
    (séparées par ';' ou ',') en ignorant les entrées vides."""
    if not texte:
        return []
    separateur = ";" if ";" in texte else ","
    return [v.strip() for v in texte.split(separateur) if v.strip()]


def _normaliser_url(valeur: str) -> str:
    """Ajoute un schéma https:// par défaut si l'utilisateur n'en a pas saisi."""
    valeur = valeur.strip()
    if not valeur or valeur.startswith(("http://", "https://")):
        return valeur
    return f"https://{valeur}"


def _normaliser_linkedin(valeur: str) -> str:
    """Accepte un nom d'utilisateur seul ou une URL LinkedIn complète."""
    valeur = valeur.strip()
    if not valeur:
        return ""
    if valeur.startswith(("http://", "https://")):
        return valeur
    if "linkedin.com" in valeur:
        return f"https://{valeur}"
    return f"https://www.linkedin.com/in/{valeur.strip('/')}"


@dataclass
class VCard:
    """Informations d'un contact, destinées à être encodées dans un QR code."""

    prenom: str = ""
    nom: str = ""
    societe: str = ""
    titre: str = ""
    emails: list[str] = field(default_factory=list)
    mobiles_personnels: list[str] = field(default_factory=list)
    mobiles_professionnels: list[str] = field(default_factory=list)
    mobile_secondaire: str = ""
    telephones_domicile: list[str] = field(default_factory=list)
    telephones_travail: list[str] = field(default_factory=list)
    telephones_fax: list[str] = field(default_factory=list)
    adresse: str = ""
    url: str = ""
    linkedin: str = ""
    note: str = ""

    @classmethod
    def depuis_champs(
        cls,
        prenom: str,
        nom: str,
        societe: str,
        titre: str,
        emails: str,
        mobiles_personnels: str,
        mobiles_professionnels: str,
        mobile_secondaire: str,
        telephones_domicile: str,
        telephones_travail: str,
        telephones_fax: str,
        adresse: str,
        url: str,
        linkedin: str,
        note: str,
    ) -> "VCard":
        """Construit une VCard à partir des champs texte bruts du formulaire."""
        return cls(
            prenom=prenom.strip(),
            nom=nom.strip(),
            societe=societe.strip(),
            titre=titre.strip(),
            emails=_valeurs_multiples(emails),
            mobiles_personnels=_valeurs_multiples(mobiles_personnels),
            mobiles_professionnels=_valeurs_multiples(mobiles_professionnels),
            mobile_secondaire=mobile_secondaire.strip(),
            telephones_domicile=_valeurs_multiples(telephones_domicile),
            telephones_travail=_valeurs_multiples(telephones_travail),
            telephones_fax=_valeurs_multiples(telephones_fax),
            adresse=adresse.strip(),
            url=_normaliser_url(url),
            linkedin=_normaliser_linkedin(linkedin),
            note=note.strip(),
        )

    def est_vide(self) -> bool:
        return not (
            self.prenom
            or self.nom
            or self.societe
            or self.titre
            or self.emails
            or self.mobiles_personnels
            or self.mobiles_professionnels
            or self.mobile_secondaire
            or self.telephones_domicile
            or self.telephones_travail
            or self.telephones_fax
            or self.adresse
            or self.url
            or self.linkedin
            or self.note
        )

    def to_vcard_string(self) -> str:
        """Sérialise le contact au format vCard 3.0."""
        lignes = ["BEGIN:VCARD", "VERSION:3.0"]

        lignes.append(f"N:{_escape(self.nom)};{_escape(self.prenom)};;;")
        nom_complet = " ".join(p for p in (self.prenom, self.nom) if p)
        lignes.append(f"FN:{_escape(nom_complet)}")

        if self.societe:
            lignes.append(f"ORG:{_escape(self.societe)}")

        if self.titre:
            lignes.append(f"TITLE:{_escape(self.titre)}")

        for mobile in self.mobiles_personnels:
            lignes.append(f"TEL;TYPE=CELL,HOME:{_escape(mobile)}")

        for mobile in self.mobiles_professionnels:
            lignes.append(f"TEL;TYPE=CELL,WORK:{_escape(mobile)}")

        if self.mobile_secondaire:
            lignes.append(f"TEL;TYPE=CELL:{_escape(self.mobile_secondaire)}")

        for telephone in self.telephones_domicile:
            lignes.append(f"TEL;TYPE=HOME,VOICE:{_escape(telephone)}")

        for telephone in self.telephones_travail:
            lignes.append(f"TEL;TYPE=WORK,VOICE:{_escape(telephone)}")

        for fax in self.telephones_fax:
            lignes.append(f"TEL;TYPE=FAX:{_escape(fax)}")

        for email in self.emails:
            lignes.append(f"EMAIL;TYPE=INTERNET:{_escape(email)}")

        if self.adresse:
            lignes.append(f"ADR;TYPE=HOME:;;{_escape(self.adresse)};;;;")

        if self.url:
            lignes.append(f"URL:{_escape(self.url)}")

        if self.linkedin:
            lignes.append(f"X-SOCIALPROFILE;TYPE=linkedin:{_escape(self.linkedin)}")

        if self.note:
            lignes.append(f"NOTE:{_escape(self.note)}")

        lignes.append("END:VCARD")
        return "\r\n".join(lignes) + "\r\n"
