# COMPILE_PREFABS
# Taken and modified from SplitGuides
from prefab_classes import prefab, attribute
import os
from pathlib import Path

base_path = Path(__file__).parents[1]

settings_file = Path(base_path / "settings.json")
default_template_folder = Path(base_path / "templates")
default_static_folder = Path(base_path / "static")
user_path = str(Path(os.path.expanduser("~")) / "Documents")


@prefab(compile_prefab=True, compile_fallback=True)
class Settings:
    """
    Global persistent settings handler
    """

    # What file to use
    output_file = attribute(default=settings_file)

    # Networking Settings
    hostname = attribute(default="localhost")
    port = attribute(default=16834)
    # Parser Settings
    split_separator = attribute(default="")
    # User Preferences
    previous_splits = attribute(default=0)
    next_splits = attribute(default=2)
    font_size = attribute(default=20)
    font_color = attribute(default="#000000")
    background_color = attribute(default="#f1f8ff")
    # Templating
    html_template_folder = attribute(default=default_template_folder)
    html_template_file = attribute(default="desktop.html")
    css_folder = attribute(default=default_static_folder)
    css_file = attribute(default="desktop.css")
    # Window Settings
    on_top = attribute(default=False)
    width = attribute(default=800)
    height = attribute(default=800)
    notes_folder = attribute(default=user_path)

    def __prefab_post_init__(self, output_file, html_template_folder, css_folder):
        self.output_file = Path(output_file)
        self.html_template_folder = Path(html_template_folder)
        self.css_folder = Path(css_folder)
