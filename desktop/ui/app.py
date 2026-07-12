import sys

from PySide6.QtWidgets import QApplication

from .window import PatrickWindow
from .controller import PatrickController
from .server_launcher import ensure_server


def main():

    ensure_server()

    app = QApplication(sys.argv)

    window = PatrickWindow()

    PatrickController(window)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":

    main()