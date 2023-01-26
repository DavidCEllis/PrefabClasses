from pathlib import Path

import prefab_classes.dynamic as dynamic_prefab
from prefab_classes.compiled import get_sources_to_compare
from prefab_classes.dynamic._attribute_class_maker.regenerate_attribute import (
    GENERATED_NOTIFICATION,
)


def test_template_matches_attribute():
    prefab_dir = Path(dynamic_prefab.__file__).parent

    input_file = prefab_dir / "_attribute_class_maker" / "_attribute_template.py"
    output_file = prefab_dir / "_attribute_class.py"

    source_text, dest_text = get_sources_to_compare(
        input_file, output_file, header_comment=GENERATED_NOTIFICATION
    )

    assert source_text == dest_text
