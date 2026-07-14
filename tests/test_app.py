import page_analyzer


def test_app_at_package_level():

    assert hasattr(page_analyzer, 'app')
    
    assert 'app' in page_analyzer.__all__