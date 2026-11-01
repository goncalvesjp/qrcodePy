"""
Module de la fenêtre principale.

Formulaire de saisie d'un contact, génération du QR code vCard correspondant
et export en PNG, JPEG ou PDF.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QTableWidgetItem

from core.carte_visite import generer_carte_pixmap
from core.export import FILTRES, completer_extension, enregistrer_image
from core.qr_generator import generer_qr_pixmap
from core.ressources import version_application
from core.vcard import VCard
from gui.ui_main_window import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    """Fenêtre principale de l'application."""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._qr_pixmap = None
        self._vcard = None

        self.champs_perso_table.horizontalHeader().setStretchLastSection(True)

        self.generer_button.clicked.connect(self.handle_generer_button_click)
        self.enregistrer_button.clicked.connect(self.handle_enregistrer_button_click)
        self.carte_button.clicked.connect(self.handle_carte_button_click)
        self.champ_ajouter_button.clicked.connect(self.handle_champ_ajouter_click)
        self.champ_supprimer_button.clicked.connect(self.handle_champ_supprimer_click)
        self.action_quit.triggered.connect(self.close)
        self.action_a_propos.triggered.connect(self.handle_a_propos_click)

    def _lire_vcard_depuis_formulaire(self) -> VCard:
        return VCard.depuis_champs(
            prenom=self.prenom_edit.text(),
            nom=self.nom_edit.text(),
            societe=self.societe_edit.text(),
            titre=self.titre_edit.text(),
            emails=self.emails_edit.text(),
            mobiles_personnels=self.mobiles_perso_edit.text(),
            mobiles_professionnels=self.mobiles_pro_edit.text(),
            mobile_secondaire=self.mobile_secondaire_edit.text(),
            telephones_domicile=self.telephones_domicile_edit.text(),
            telephones_travail=self.telephones_travail_edit.text(),
            telephones_fax=self.fax_edit.text(),
            adresse=self.adresse_edit.toPlainText(),
            url=self.url_edit.text(),
            linkedin=self.linkedin_edit.text(),
            note=self.note_edit.toPlainText(),
            champs_personnalises=self._lire_champs_personnalises(),
        )

    def _lire_champs_personnalises(self) -> list[tuple[str, str]]:
        champs = []
        for ligne in range(self.champs_perso_table.rowCount()):
            item_nom = self.champs_perso_table.item(ligne, 0)
            item_valeur = self.champs_perso_table.item(ligne, 1)
            champs.append((
                item_nom.text() if item_nom else "",
                item_valeur.text() if item_valeur else "",
            ))
        return champs

    def handle_champ_ajouter_click(self):
        """Ajoute une ligne vide au tableau des champs personnalisés."""
        ligne = self.champs_perso_table.rowCount()
        self.champs_perso_table.insertRow(ligne)
        self.champs_perso_table.setItem(ligne, 0, QTableWidgetItem())
        self.champs_perso_table.setItem(ligne, 1, QTableWidgetItem())
        self.champs_perso_table.setCurrentCell(ligne, 0)
        self.champs_perso_table.editItem(self.champs_perso_table.item(ligne, 0))

    def handle_champ_supprimer_click(self):
        """Supprime la ou les lignes sélectionnées du tableau des champs personnalisés."""
        lignes = {index.row() for index in self.champs_perso_table.selectedIndexes()}
        for ligne in sorted(lignes, reverse=True):
            self.champs_perso_table.removeRow(ligne)

    def handle_generer_button_click(self):
        """Construit la vCard depuis le formulaire et affiche son QR code."""
        vcard = self._lire_vcard_depuis_formulaire()
        if vcard.est_vide():
            QMessageBox.warning(
                self, "Champs manquants", "Veuillez renseigner au moins un champ du contact."
            )
            return

        self._vcard = vcard
        self._qr_pixmap = generer_qr_pixmap(
            vcard.to_vcard_string(),
            texte_haut=self.texte_haut_edit.text(),
            texte_bas=self.texte_bas_edit.text(),
        )
        self.qr_preview_label.setPixmap(
            self._qr_pixmap.scaled(
                self.qr_preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
        )
        self.enregistrer_button.setEnabled(True)
        self.carte_button.setEnabled(True)
        self.statusbar.showMessage("QR code généré.", 5000)

    def handle_enregistrer_button_click(self):
        """Enregistre le QR code généré en PNG, JPEG ou PDF."""
        if self._qr_pixmap is None:
            return
        self._enregistrer_pixmap(self._qr_pixmap, "Enregistrer le QR code", "qrcode.png")

    def handle_carte_button_click(self):
        """Enregistre la carte de visite (QR code + coordonnées) en PNG, JPEG ou PDF."""
        if self._vcard is None:
            return
        carte_pixmap = generer_carte_pixmap(self._vcard)
        self._enregistrer_pixmap(carte_pixmap, "Enregistrer la carte de visite", "carte-de-visite.png")

    def _enregistrer_pixmap(self, pixmap, titre_dialogue: str, nom_fichier_defaut: str):
        chemin, filtre = QFileDialog.getSaveFileName(self, titre_dialogue, nom_fichier_defaut, FILTRES)
        if not chemin:
            return

        chemin = completer_extension(chemin, filtre)

        try:
            enregistrer_image(pixmap, chemin)
        except OSError:
            QMessageBox.critical(self, "Erreur", "Impossible d'enregistrer le fichier.")
            return

        self.statusbar.showMessage(f"Fichier enregistré : {chemin}", 5000)

    def handle_a_propos_click(self):
        """Affiche les informations sur l'application."""
        QMessageBox.about(
            self,
            "À propos de QR Visite",
            "<h3>QR Visite</h3>"
            f"<p>Version {version_application()}</p>"
            "<p>Application de bureau PyQt6 pour générer des QR codes : "
            "carte de contact (vCard), texte personnalisé au-dessus/en-dessous, "
            "export en PNG, JPEG ou PDF.</p>",
        )
