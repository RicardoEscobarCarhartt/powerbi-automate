"""This test module contains unit tests for the popup module."""

from unittest.mock import patch, Mock

import pytest

from carhartt_pbi_automate.popup import create_test_popup, detect_popup_window


@patch("carhartt_pbi_automate.popup.Application")
@pytest.mark.unit
def test_create_test_popup(mock_application):
    """Test the create_test_popup function."""
    # Mock the Application class
    mock_application_instance = mock_application.return_value

    # Mock a return value for the start method
    mock_application_instance.start.return_value = Mock()

    # Call the create_test_popup function
    create_test_popup()

    # Assert that the start method was called with the correct argument
    mock_application_instance.start.assert_called_once_with("notepad.exe")


@patch("carhartt_pbi_automate.popup.Application")
@pytest.mark.unit
def test_detect_popup_window(mock_application):
    """Test the detect_popup_window function."""
    # Define a list of window titles to search for
    window_titles = ["Title1", "Title2", "Title3"]

    # Mock the Application class
    mock_application_instance = mock_application.return_value

    # Mock a return value for the connect method
    mock_application_instance.connect.return_value = mock_application_instance

    # Mock a return value for the window method
    mock_popup_window = mock_application_instance.window.return_value

    # Call the detect_popup_window function
    detect_popup_window(window_titles)

    # Assert that the connect method was called with the correct argument
    mock_application_instance.connect.assert_called_once_with(
        title_re="Title1"
    )

    # Assert that the window method was called with the correct argument
    mock_application_instance.window.assert_called_once_with(title_re="Title1")

    # Assert that the exists method was called on the popup window
    mock_popup_window.exists.assert_called_once()
