"""
Module de la fenêtre principale.

Formulaire de saisie d'un contact, génération du QR code vCard correspondant
et export en PNG, JPEG ou PDF.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from core.export import FILTRES, completer_extension, enregistrer_qr
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

        self.generer_button.clicked.connect(self.handle_generer_button_click)
        self.enregistrer_button.clicked.connect(self.handle_enregistrer_button_click)
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
            telephones_domicile=self.telephones_domicile_edit.text(),
            telephones_travail=self.telephones_travail_edit.text(),
            telephones_fax=self.fax_edit.text(),
            adresse=self.adresse_edit.toPlainText(),
            url=self.url_edit.text(),
            linkedin=self.linkedin_edit.text(),
            note=self.note_edit.toPlainText(),
        )

    def handle_generer_button_click(self):
        """Construit la vCard depuis le formulaire et affiche son QR code."""
        vcard = self._lire_vcard_depuis_formulaire()
        if vcard.est_vide():
            QMessageBox.warning(
                self, "Champs manquants", "Veuillez renseigner au moins un champ du contact."
            )
            return

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
        self.statusbar.showMessage("QR code généré.", 5000)

    def handle_enregistrer_button_click(self):
        """Enregistre le QR code généré en PNG, JPEG ou PDF."""
        if self._qr_pixmap is None:
            return

        chemin, filtre = QFileDialog.getSaveFileName(
            self, "Enregistrer le QR code", "qrcode.png", FILTRES
        )
        if not chemin:
            return

        chemin = completer_extension(chemin, filtre)

        try:
            enregistrer_qr(self._qr_pixmap, chemin)
        except OSError:
            QMessageBox.critical(self, "Erreur", "Impossible d'enregistrer le fichier.")
            return

        self.statusbar.showMessage(f"QR code enregistré : {chemin}", 5000)

    def handle_a_propos_click(self):
        """Affiche les informations sur l'application."""
        QMessageBox.about(
            self,
            "À propos de Générateur de QR Codes",
            "<h3>Générateur de QR Codes</h3>"
            f"<p>Version {version_application()}</p>"
            "<p>Application de bureau PyQt6 pour générer des QR codes : "
            "carte de contact (vCard), texte personnalisé au-dessus/en-dessous, "
            "export en PNG, JPEG ou PDF.</p>",
        )
