"""This test module contains unit tests for the popup module."""

from unittest.mock import patch
import sys
from pathlib import Path

import pytest

from carhartt_pbi_automate import get_logger
from carhartt_pbi_automate.popup import create_test_popup, detect_popup_window
