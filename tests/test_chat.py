from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.backend.Bots import chat


def test_invalid_model_decision_falls_back_to_local_result():
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='["unexpected"]'))]
    )
    client = Mock()
    client.chat.completions.create.return_value = response

    with patch.object(chat, "client", client):
        decision = chat.decide_and_extract_booking("Hola, ¿qué tal?")

    assert decision["action"] == "CHAT"
    assert isinstance(decision["booking"], dict)
