from pathlib import Path

from prefab_classes.compiled import rewrite_to_py


TEMPLATE_FILE = Path(__file__).parent / "_attribute_template.py"
OUTPUT_FILE = Path(__file__).parents[1] / "_attribute_class.py"


GENERATED_NOTIFICATION = """
# DO NOT MANUALLY EDIT THIS FILE
# THIS MODULE IS AUTOMATICALLY GENERATED FROM _attribute_template.py
# BY regenerate_attribute.py
# MODIFY THOSE MODULES AND RERUN regenerate_attribute.py
""".strip()


def generate_source():
    rewrite_to_py(TEMPLATE_FILE, OUTPUT_FILE, header_comment=GENERATED_NOTIFICATION)


if __name__ == "__main__":
    generate_source()
