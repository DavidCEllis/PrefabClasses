# DO NOT MANUALLY EDIT THIS FILE
# MODULE: example_to_compile_expected_temp.py
# GENERATED FROM: example_to_compile.py

import os
from pathlib import Path
base_path = Path(__file__).parents[1]
settings_file = Path(base_path / 'settings.json')
default_template_folder = Path(base_path / 'templates')
default_static_folder = Path(base_path / 'static')
user_path = str(Path(os.path.expanduser('~')) / 'Documents')

class Settings:
    """
    Global persistent settings handler
    """
    COMPILED = True
    PREFAB_FIELDS = ['output_file', 'hostname', 'port', 'split_separator', 'previous_splits', 'next_splits', 'font_size', 'font_color', 'background_color', 'html_template_folder', 'html_template_file', 'css_folder', 'css_file', 'on_top', 'width', 'height', 'notes_folder']
    __match_args__ = ('output_file', 'hostname', 'port', 'split_separator', 'previous_splits', 'next_splits', 'font_size', 'font_color', 'background_color', 'html_template_folder', 'html_template_file', 'css_folder', 'css_file', 'on_top', 'width', 'height', 'notes_folder')

    def __init__(self, output_file=settings_file, hostname='localhost', port=16834, split_separator='', previous_splits=0, next_splits=2, font_size=20, font_color='#000000', background_color='#f1f8ff', html_template_folder=default_template_folder, html_template_file='desktop.html', css_folder=default_static_folder, css_file='desktop.css', on_top=False, width=800, height=800, notes_folder=user_path):
        self.hostname = hostname
        self.port = port
        self.split_separator = split_separator
        self.previous_splits = previous_splits
        self.next_splits = next_splits
        self.font_size = font_size
        self.font_color = font_color
        self.background_color = background_color
        self.html_template_file = html_template_file
        self.css_file = css_file
        self.on_top = on_top
        self.width = width
        self.height = height
        self.notes_folder = notes_folder
        self.__prefab_post_init__(output_file=output_file, html_template_folder=html_template_folder, css_folder=css_folder)

    def __repr__(self):
        return f'{type(self).__qualname__}(output_file={self.output_file!r}, hostname={self.hostname!r}, port={self.port!r}, split_separator={self.split_separator!r}, previous_splits={self.previous_splits!r}, next_splits={self.next_splits!r}, font_size={self.font_size!r}, font_color={self.font_color!r}, background_color={self.background_color!r}, html_template_folder={self.html_template_folder!r}, html_template_file={self.html_template_file!r}, css_folder={self.css_folder!r}, css_file={self.css_file!r}, on_top={self.on_top!r}, width={self.width!r}, height={self.height!r}, notes_folder={self.notes_folder!r})'

    def __eq__(self, other):
        return (self.output_file, self.hostname, self.port, self.split_separator, self.previous_splits, self.next_splits, self.font_size, self.font_color, self.background_color, self.html_template_folder, self.html_template_file, self.css_folder, self.css_file, self.on_top, self.width, self.height, self.notes_folder) == (other.output_file, other.hostname, other.port, other.split_separator, other.previous_splits, other.next_splits, other.font_size, other.font_color, other.background_color, other.html_template_folder, other.html_template_file, other.css_folder, other.css_file, other.on_top, other.width, other.height, other.notes_folder) if self.__class__ == other.__class__ else NotImplemented

    def __prefab_post_init__(self, output_file, html_template_folder, css_folder):
        self.output_file = Path(output_file)
        self.html_template_folder = Path(html_template_folder)
        self.css_folder = Path(css_folder)