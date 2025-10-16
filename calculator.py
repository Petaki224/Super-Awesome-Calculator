from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QIcon
from updater import check_for_updates
import sys

VERSION = "1.1"
SIDEBAR_WIDTH = 220

def setup_sidebar(pages: QtWidgets.QStackedWidget, width: int = SIDEBAR_WIDTH) -> tuple[QtWidgets.QFrame, callable]:
    """
    Maakt de sidebar + animatie.
    De knoppen wisselen tussen de pagina's van de QStackedWidget.
    """
    sidebar = QtWidgets.QFrame()
    sidebar.setMinimumWidth(0)
    sidebar.setMaximumWidth(0)
    sidebar.setFrameShape(QtWidgets.QFrame.StyledPanel)
    sidebar.setFrameShadow(QtWidgets.QFrame.Raised)

    layout = QtWidgets.QVBoxLayout(sidebar)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(8)

    layout.addWidget(QtWidgets.QLabel("Menu"))

    btn_calc = QtWidgets.QPushButton("Calculator")
    btn_history = QtWidgets.QPushButton("History")
    btn_settings = QtWidgets.QPushButton("Settings")

    layout.addWidget(btn_calc)
    layout.addWidget(btn_history)
    layout.addWidget(btn_settings)
    layout.addStretch()

    # Tab switching logic
    btn_calc.clicked.connect(lambda: pages.setCurrentIndex(0))
    btn_history.clicked.connect(lambda: pages.setCurrentIndex(1))
    btn_settings.clicked.connect(lambda: pages.setCurrentIndex(2))

    # Slide animation
    is_open = {"v": False}
    anim = QtCore.QPropertyAnimation(sidebar, b"maximumWidth")
    anim.setDuration(220)
    anim.setEasingCurve(QtCore.QEasingCurve.InOutCubic)

    def toggle_sidebar():
        start = sidebar.maximumWidth()
        end = width if not is_open["v"] else 0
        anim.stop()
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.start()
        is_open["v"] = not is_open["v"]

    return sidebar, toggle_sidebar


def main():
    app = QtWidgets.QApplication(sys.argv)

    root = QtWidgets.QWidget()
    root.setWindowTitle(f"Super Awesome Calculator v{VERSION}")
    root.setWindowIcon(QIcon("SAC_icon.png"))

    # --- Hoofd layout: [SIDEBAR][STACKED PAGES] ---
    hroot = QtWidgets.QHBoxLayout(root)
    hroot.setContentsMargins(8, 8, 8, 8)
    hroot.setSpacing(8)

    # QStackedWidget = container met meerdere "pagina's"
    pages = QtWidgets.QStackedWidget()

    # ========== Pagina 0: Calculator ==========
    calc_page = QtWidgets.QWidget()
    calc_layout = QtWidgets.QVBoxLayout(calc_page)

    # Top bar met toggle-knop + entry
    top = QtWidgets.QHBoxLayout()
    top.setSpacing(6)

    btn_sidebar = QtWidgets.QToolButton()
    btn_sidebar.setText("☰")
    btn_sidebar.setFixedSize(32, 32)
    btn_sidebar.setToolTip("Open/close menu")

    entry = QtWidgets.QLineEdit()
    entry.setFixedHeight(40)
    entry.setStyleSheet("font-size: 20px;")

    top.addWidget(btn_sidebar, 0)
    top.addWidget(entry, 1)
    calc_layout.addLayout(top)

    # Buttons
    button_frame = QtWidgets.QWidget()
    calc_layout.addWidget(button_frame)
    create_buttons(button_frame, entry)

    # ========== Pagina 1: History ==========
    history_page = QtWidgets.QWidget()
    h_layout = QtWidgets.QVBoxLayout(history_page)
    h_layout.addWidget(QtWidgets.QLabel("History tab (comming later :P)"))
    h_layout.addStretch()

    # ========== Pagina 2: Settings ==========
    settings_page = QtWidgets.QWidget()
    s_layout = QtWidgets.QVBoxLayout(settings_page)
    s_layout.addWidget(QtWidgets.QLabel("Settings tab"))
    s_layout.addStretch()

    btn_check = QtWidgets.QPushButton("Check for updates")
    btn_check.clicked.connect(lambda: check_for_updates(root, VERSION, "Petaki224/Super-Awesome-Calculator"))
    s_layout.addWidget(btn_check)


    # Voeg pagina’s toe aan stack
    pages.addWidget(calc_page)     # index 0
    pages.addWidget(history_page)  # index 1
    pages.addWidget(settings_page) # index 2

    # Sidebar aanmaken met verwijzing naar pages
    sidebar, toggle_sidebar = setup_sidebar(pages)

    # Sidebarknop koppelen
    btn_sidebar.clicked.connect(toggle_sidebar)

    # Voeg alles samen
    hroot.addWidget(sidebar, 0)
    hroot.addWidget(pages, 1)

    root.show()
    sys.exit(app.exec())


def create_buttons(button_frame, entry):
    labels = ["7", "8", "9", "+",
              "4", "5", "6", "-",
              "1", "2", "3", "x",
              "0", "C", "=", "/",
              ".", "(", ")", "<--"]

    grid = QtWidgets.QGridLayout(button_frame)
    row = 0
    column = 0
    for i, label in enumerate(labels):
        btn = QtWidgets.QPushButton(f"{label}")
        btn.setStyleSheet("font-size: 16px; padding: 8px;")
        btn.setMinimumWidth(100)
        btn.setMinimumHeight(40)
        btn.clicked.connect(lambda checked=False, x=label: on_button_click(x, entry))
        grid.addWidget(btn, row, column)
        column += 1
        if column == 4:
            column = 0
            row += 1


def on_button_click(value, entry: QtWidgets.QLineEdit):
    match value:
        case "+": entry.insert("+")
        case "-": entry.insert("-")
        case "x": entry.insert("*")
        case "/": entry.insert("/")
        case ".": entry.insert(".")
        case "C": entry.clear()
        case "(": entry.insert("(")
        case ")": entry.insert(")")
        case "<--": entry.backspace()
        case "=": calculate(entry)
        case _:
            if value.isdigit():
                entry.insert(f"{value}")


def calculate(entry: QtWidgets.QLineEdit):
    som = entry.text()
    if not som.strip():
        return
    try:
        entry.clear()
        entry.insert(str(eval(som)))
    except Exception:
        entry.clear()
        entry.insert("leuk geprobeerd! nu weer stofzuigen.")


if __name__ == "__main__":
    main()
