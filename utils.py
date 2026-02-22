import os
import sys


def resource_path(filename: str) -> str:
    """Geeft het absolute pad naar een asset.
    Werkt zowel bij normale run als PyInstaller --onefile build."""
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller extraheert assets naar een tijdelijke map
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def highscore_path() -> str:
    """Slaat highscore op in de home directory van de gebruiker,
    zodat het zowel bij een normale run als packaged build werkt."""
    home = os.path.expanduser("~")
    return os.path.join(home, ".stay_in_lane_highscore.json")