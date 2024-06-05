import time
from typing import List
from pathlib import Path
import logging
import traceback
import pywinauto
from pywinauto.application import Application

# Import the get_logger function from the get_logger module if the module is in
# the same directory as the current script. Otherwise, import the get_logger
# function from the carhartt_pbi_automate package. This is done because the
# get_logger module is not part of the package if it is run as a script.
try:
    from get_logger import get_logger
except ImportError:
    from carhartt_pbi_automate.get_logger import get_logger


# Create a logger object
root_path = Path(__file__).parent.parent
log = get_logger(
    __name__,
    logfile=root_path / "logs" / "popup.log",
    console_output=True,
    level=logging.DEBUG,
)


def create_test_popup():
    # Create a simple pop-up window
    app = Application().start(
        "notepad.exe"
    )  # Replace with the path to your application
    app.Notepad.menu_select("Ayuda->Acerca del Bloc de Notas")


def detect_popup_window(window_title: List[str]):
    # Wait for the pop-up window to appear
    for title in window_title:
        try:
            app = Application().connect(title_re=title)
            popup_window = app.window(title_re=title)
            break
        except pywinauto.findwindows.ElementNotFoundError as error:
            stacktrace = traceback.format_exc()
            log.error("Traceback: %s", stacktrace)
            log.error("ElementNotFoundError: %s", error)
            popup_window = None
        except Exception as error:
            stacktrace = traceback.format_exc()
            log.error("Traceback: %s", stacktrace)
            log.error("Error: %s", error)
            popup_window = None

    if popup_window.exists():
        log.info("Pop-up window detected! Title: %s", popup_window.window_text())
        # Set focus to the pop-up window
        popup_window.set_focus()

        # Press tab key to navigate through the pop-up window, then press Enter
        time.sleep(1)
        popup_window.type_keys("{TAB}")
        time.sleep(1)
        popup_window.type_keys("{ENTER}")
        log.info("Pop-up window closed.")
    else:
        log.info("Pop-up window not found.")


if __name__ == "__main__":
    titles = ["Acerca de Bloc de notas", "About Notepad"]
    create_test_popup()
    time.sleep(2)  # Wait for the pop-up to appear (adjust as needed)
    detect_popup_window(titles)
