from fleur import emit
from fleur.ui import Notice


def test_announcement_priority_is_independent_of_notice_variant() -> None:
    polite = emit(Notice("Failed to save", variant="error").__compile__())
    urgent = emit(Notice("Connection lost", announce="assertive").__compile__())
    silent = emit(Notice("Saved", variant="success", announce="off").__compile__())

    assert 'role: "status"' in polite
    assert 'role: "alert"' in urgent
    assert 'role: "status"' not in silent and 'role: "alert"' not in silent
