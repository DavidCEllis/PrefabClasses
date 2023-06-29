def test_using_correct_importers(importer):
    # Check that the test config does actually use both importers

    from config_check import ConfigCheck  # noqa

    assert ConfigCheck.COMPILED == importer, "Configuration is not using the correct importer"
