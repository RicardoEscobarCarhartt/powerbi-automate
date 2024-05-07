import time
from pywinauto.application import Application


def create_test_popup():
    # Create a simple pop-up window
    app = Application().start(
        "notepad.exe"
    )  # Replace with the path to your application
    app.Notepad.menu_select("Ayuda->Acerca del Bloc de Notas")


def detect_popup_window(window_title=".*Iniciar sesión en la cuenta.*"):
    # Wait for the pop-up window to appear
    app = Application().connect(title_re=window_title)
    popup_window = app.window(title_re=window_title)

    if popup_window.exists():
        print(f"Pop-up window detected! Title: {popup_window.window_text()}")
        # Set focus to the pop-up window
        popup_window.set_focus()

        # Press tab key to navigate through the pop-up window, then press Enter
        # Introduce a delay
        time.sleep(1)

        # Send the keys
        popup_window.type_keys("{TAB}")
        time.sleep(1)
        popup_window.type_keys("{ENTER}")
    else:
        print("Pop-up window not found.")


if __name__ == "__main__":
    create_test_popup()
    time.sleep(2)  # Wait for the pop-up to appear (adjust as needed)
    detect_popup_window()
