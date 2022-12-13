from pathlib import Path

import prefab_classes.dynamic._attribute_class as attribute_module
from prefab_classes.dynamic._attribute_class_maker.regenerate_attribute import (
    generate_attribute_source,
)


def test_template_matches_attribute():
    output_file = Path(attribute_module.__file__)

    template_output = generate_attribute_source()

    assert template_output == output_file.read_text()
