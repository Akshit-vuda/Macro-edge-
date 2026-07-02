"""
Smoke tests for MacroEdge services and ML modules.
Verifies that all files and classes can be loaded without syntax/import errors.
"""


def test_import_services() -> None:
    """
    Test that all backend service modules can be imported without raising errors.
    """
    import backend.services.claude_brain as cb
    import backend.services.data_loader as dl
    import backend.services.database as db
    import backend.services.news_intelligence as ni
    import backend.services.risk_management as rm
    import backend.services.trading as t
    
    assert cb is not None
    assert dl is not None
    assert db is not None
    assert ni is not None
    assert rm is not None
    assert t is not None


def test_import_ml() -> None:
    """
    Test that all backend ML modules can be imported without raising errors.
    """
    import backend.ml.models as m
    import backend.ml.technical_analysis as ta
    import backend.ml.training_pipeline as tp
    
    assert m is not None
    assert ta is not None
    assert tp is not None


def test_import_main() -> None:
    """
    Test that the main API entrypoint module can be imported without raising errors.
    """
    import main
    assert main is not None
