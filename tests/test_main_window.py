"""Tests de la fenêtre principale."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidgetItem

from core.main_window import MainWindow


def test_main_window_creation():
    """La fenêtre principale doit s'instancier sans erreur."""
    window = MainWindow()
    assert window.windowTitle() == "QR Visite"


def test_generer_button_sans_champ_affiche_avertissement(qtbot, monkeypatch):
    """Générer sans aucun champ rempli ne doit pas planter (avertissement affiché)."""
    avertissements = []
    monkeypatch.setattr(
        "core.main_window.QMessageBox.warning",
        lambda *args, **kwargs: avertissements.append(True),
    )

    window = MainWindow()
    qtbot.addWidget(window)

    qtbot.mouseClick(window.generer_button, Qt.MouseButton.LeftButton)

    assert avertissements == [True]
    assert not window.enregistrer_button.isEnabled()


def test_generer_button_avec_champs_affiche_le_qr_code(qtbot):
    """Avec au moins un champ rempli, le QR code est généré et affichable."""
    window = MainWindow()
    qtbot.addWidget(window)

    window.prenom_edit.setText("Jean")
    window.nom_edit.setText("Dupont")
    window.emails_edit.setText("jean.dupont@exemple.com")

    qtbot.mouseClick(window.generer_button, Qt.MouseButton.LeftButton)

    assert window._qr_pixmap is not None
    assert not window.qr_preview_label.pixmap().isNull()
    assert window.enregistrer_button.isEnabled()
    assert window.carte_button.isEnabled()


def test_carte_button_enregistre_la_carte_de_visite(qtbot, monkeypatch, tmp_path):
    """Le bouton carte de visite doit proposer un fichier et l'enregistrer."""
    chemin = tmp_path / "carte.png"
    monkeypatch.setattr(
        "core.main_window.QFileDialog.getSaveFileName",
        lambda *args, **kwargs: (str(chemin), "Image PNG (*.png)"),
    )

    window = MainWindow()
    qtbot.addWidget(window)

    window.prenom_edit.setText("Jean")
    window.nom_edit.setText("Dupont")
    window.emails_edit.setText("jean.dupont@exemple.com")
    qtbot.mouseClick(window.generer_button, Qt.MouseButton.LeftButton)

    qtbot.mouseClick(window.carte_button, Qt.MouseButton.LeftButton)

    assert chemin.exists()


def test_champ_ajouter_button_insere_une_ligne(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    assert window.champs_perso_table.rowCount() == 0

    qtbot.mouseClick(window.champ_ajouter_button, Qt.MouseButton.LeftButton)

    assert window.champs_perso_table.rowCount() == 1


def test_champ_supprimer_button_retire_la_ligne_selectionnee(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    window.champs_perso_table.insertRow(0)
    window.champs_perso_table.setItem(0, 0, QTableWidgetItem("Skype"))
    window.champs_perso_table.setItem(0, 1, QTableWidgetItem("jdupont"))
    window.champs_perso_table.insertRow(1)
    window.champs_perso_table.setItem(1, 0, QTableWidgetItem("Telegram"))
    window.champs_perso_table.setItem(1, 1, QTableWidgetItem("@jdupont"))

    window.champs_perso_table.selectRow(0)
    qtbot.mouseClick(window.champ_supprimer_button, Qt.MouseButton.LeftButton)

    assert window.champs_perso_table.rowCount() == 1
    assert window.champs_perso_table.item(0, 0).text() == "Telegram"


def test_champs_personnalises_inclus_dans_la_vcard_generee(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    window.prenom_edit.setText("Jean")
    window.champs_perso_table.insertRow(0)
    window.champs_perso_table.setItem(0, 0, QTableWidgetItem("Skype"))
    window.champs_perso_table.setItem(0, 1, QTableWidgetItem("jdupont"))

    qtbot.mouseClick(window.generer_button, Qt.MouseButton.LeftButton)

    assert window._vcard.champs_personnalises == [("Skype", "jdupont")]
    assert "X-SKYPE:jdupont" in window._vcard.to_vcard_string()


def test_action_a_propos_affiche_le_dialogue(qtbot, monkeypatch):
    """L'action de menu « À propos » doit ouvrir la boîte de dialogue dédiée."""
    appels = []
    monkeypatch.setattr(
        "core.main_window.QMessageBox.about",
        lambda *args, **kwargs: appels.append(args),
    )

    window = MainWindow()
    qtbot.addWidget(window)

    window.action_a_propos.trigger()

    assert len(appels) == 1
    assert "QR Visite" in appels[0][2]
