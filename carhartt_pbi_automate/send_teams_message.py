"""This module prepares and sends a message to a Microsoft Teams channel using
the incoming webhook URL"""

from typing import Dict

import pymsteams

try:
    from get_logger import get_logger
except ImportError:
    from carhartt_pbi_automate.get_logger import get_logger


# Initialize logger
log = get_logger(__name__, logfile=f"logs/{__name__}.log")


def send_ok_teams_message(args: Dict[str, str]) -> bool:
    """
    Send a message to a Microsoft Teams channel using the incoming webhook URL
    Args:
        args (Dict): A dictionary containing the following keys:
            teams_webhook_url (str): The incoming webhook URL for the Teams channel
            color (str): The color of the message card
            notification_title (str): The title of the message card
            message (str): The message body
            section_title (str): The title of the section
            section_text (str): The text of the section
    Returns:
        response (requests.models.Response): The response from the webhook
        (True if successful, False if failed)
    """
    # Create the connectorcard object
    my_teams_message = pymsteams.connectorcard(args["teams_webhook_url"])

    # Create the message
    my_teams_message.color(args["color"])
    my_teams_message.title(args["notification_title"])
    my_teams_message.text(args["message"])

    # create the section
    my_message_section = pymsteams.cardsection()

    # Section Title
    my_message_section.title(args["section_title"])

    # Section Text
    my_message_section.text(args["section_text"])

    # Add your section to the connector card object before sending
    my_teams_message.addSection(my_message_section)

    # Log the contents of the message
    log.info("OK message sent.")

    return my_teams_message.send()


def send_fail_teams_message(args: Dict[str, str]) -> bool:
    """
    Send a message to a Microsoft Teams channel using the incoming webhook URL
    Args:
        args (Dict): A dictionary containing the following keys:
            teams_webhook_url (str): The incoming webhook URL for the Teams channel
            color (str): The color of the message card
            notification_title (str): The title of the message card
            message (str): The message body
            compare_report (str): The str containing the comparison report
    Returns:
        response (requests.models.Response): The response from the webhook
        (True if successful, False if failed)
    """
    # Create the connectorcard object
    my_teams_message = pymsteams.connectorcard(args["teams_webhook_url"])

    # Create the message
    my_teams_message.color(args["color"])
    my_teams_message.title(args["notification_title"])
    my_teams_message.text(args["message"])

    # create the sections
    compare_report_section = pymsteams.cardsection()

    # Section Titles
    compare_report_section.title("Comparison Report")

    # Section Texts, containing the table markdown content
    compare_report_section.text("```\n" + args["compare_report"] + "\n```")

    # Add your section to the connector card object before sending
    my_teams_message.addSection(compare_report_section)

    # Log the contents of the message
    log.info("Fail message sent.")

    return my_teams_message.send()
