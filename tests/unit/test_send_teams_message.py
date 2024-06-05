"""This module contains unit tests for the send_teams_message module."""

from unittest.mock import patch

import pytest

from carhartt_pbi_automate.send_teams_message import (
    send_ok_teams_message,
    send_fail_teams_message,
)


@patch("carhartt_pbi_automate.send_teams_message.pymsteams.connectorcard")
@pytest.mark.unit
def test_send_ok_teams_message(mock_connectorcard):
    """Test the send_ok_teams_message function."""
    args = {
        "teams_webhook_url": "https://outlook.office.com/webhook/...",
        "color": "green",
        "notification_title": "Test Notification",
        "message": "This is a test message.",
        "section_title": "Test Section",
        "section_text": "This is a test section.",
    }
    # Mock the send method of the connectorcard object
    mock_connectorcard.return_value.send.return_value = True

    # Call the send_ok_teams_message function
    response = send_ok_teams_message(args)
    assert response is True


@patch("carhartt_pbi_automate.send_teams_message.pymsteams.connectorcard")
@pytest.mark.unit
def test_send_fail_teams_message(mock_connectorcard):
    """Test the send_fail_teams_message function."""
    args = {
        "teams_webhook_url": "https://outlook.office.com/webhook/...",
        "color": "red",
        "notification_title": "Test Notification",
        "message": "This is a test message.",
        "section_title": "Test Section",
        "section_text": "This is a test section.",
        "compare_report": "This is a test comparison report.",
    }
    # Mock the send method of the connectorcard object
    mock_connectorcard.return_value.send.return_value = False

    # Call the send_fail_teams_message function
    response = send_fail_teams_message(args)
    assert response is False
