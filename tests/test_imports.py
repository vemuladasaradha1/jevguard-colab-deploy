
# pyrefly: ignore [missing-import]
# Source - https://stackoverflow.com/q/4383571
# Posted by Ivan, modified by community. See post 'Timeline' for change history
# Retrieved 2026-09-25, License - CC BY-SA 4.0

#from app.main import app




def test_imports():
    from app.tools import calculator_tool

    assert calculator_tool("25 * 48") == "1200"
