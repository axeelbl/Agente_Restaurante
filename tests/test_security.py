import csv
from unittest.mock import Mock, patch

from app.backend import csv_utils
from app.backend.booking import notifications


def test_csv_cells_cannot_become_formulas(tmp_path):
    leads_file = tmp_path / "leads.csv"
    meta = {"response_time": 0.1}
    with patch.object(csv_utils, "LEADS_FILE", leads_file):
        csv_utils.save_lead("=1+1", "@SUM(A1:A2)", meta)

    with leads_file.open(newline="", encoding="utf-8") as file_handle:
        row = list(csv.reader(file_handle))[1]
    assert row[-2:] == ["'=1+1", "'@SUM(A1:A2)"]


def test_booking_email_escapes_user_content():
    response = Mock()
    response.raise_for_status.return_value = None
    with (
        patch.object(notifications, "RESEND_API_KEY", "configured"),
        patch.object(notifications, "FROM_EMAIL", "sender@example.com"),
        patch.object(notifications.httpx, "post", return_value=response) as post,
    ):
        notifications.send_booking_email(
            "recipient@example.com",
            "<script>alert(1)</script>",
            2,
            "2026-09-20",
            "21:00",
            notes="<b>window</b>",
        )

    html = post.call_args.kwargs["json"]["html"]
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;b&gt;window&lt;/b&gt;" in html
