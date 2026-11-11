# SPDX-License-Identifier: GPL-3.0-or-later
"""
Point d'entrée de l'application.

Ce module initialise l'application PyQt6 et lance la fenêtre principale.
"""

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from core.main_window import MainWindow
from core.ressources import chemin_ressource


def main():
    """Initialise l'application PyQt6 et lance la fenêtre principale."""
    app = QApplication([])
    app.setWindowIcon(QIcon(str(chemin_ressource("assets/icon.png"))))
    try:
        window = MainWindow()
        window.show()
        app.exec()
    except Exception as e:
        print(f"Une erreur est survenue : {e}")


if __name__ == "__main__":
    main()
