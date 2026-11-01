"""Tests de la fenêtre principale."""

from PyQt6.QtCore import Qt

from core.main_window import MainWindow


def test_main_window_creation():
    """La fenêtre principale doit s'instancier sans erreur."""
    window = MainWindow()
    assert window.windowTitle() == "Générateur de QR Codes"


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
    assert "Générateur de QR Codes" in appels[0][2]
