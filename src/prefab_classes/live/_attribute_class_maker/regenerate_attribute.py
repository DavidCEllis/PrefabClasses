from pathlib import Path

from prefab_classes.compiled import preview


TEMPLATE_FILE = Path(__file__).parent / "_attribute_template.py"
OUTPUT_FILE = Path(__file__).parents[1] / "_attribute_class.py"


GENERATED_NOTIFICATION = """
# DO NOT MANUALLY EDIT THIS FILE
# THIS MODULE IS AUTOMATICALLY GENERATED FROM _attribute_template.py
# BY regenerate_attribute.py
# MODIFY THOSE MODULES AND RERUN regenerate_attribute.py
""".strip()


def generate_attribute_source():
    code = preview(TEMPLATE_FILE, use_black=False)
    # Delete the first line
    code = "\n".join(code.split("\n")[1:])

    source = f"{GENERATED_NOTIFICATION}\n\n{code}"
    return source


def write_attribute_module():
    source = generate_attribute_source()
    OUTPUT_FILE.write_text(source)


if __name__ == "__main__":
    write_attribute_module()
