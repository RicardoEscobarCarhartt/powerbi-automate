import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from dotenv import load_dotenv


# Load the environment variables from the .env file
load_dotenv()


def send_email(subject, body, to_address, dataframe: pd.DataFrame):
    """Send an email using Outlook SMTP server."""
    # Outlook SMTP server details
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    smtp_username = os.getenv("OUTLOOK_USERNAME")
    smtp_password = os.getenv("OUTLOOK_PASSWORD")

    # Sender and recipient email addresses
    sender_email = os.getenv("OUTLOOK_SENDER_EMAIL")
    recipient_email = to_address

    # Convert the Pandas DataFrame to an HTML table
    table_html = dataframe.to_html(index=False)

    # Create the html email body with the table
    html_body = f"""This is an automated email. Please do not reply to this email.\n\n{body}\n\n{table_html}"""

    # Create the MIME object
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    # Attach the HTML table as the email body
    msg.attach(MIMEText(html_body, "html"))

    # Establish a connection to the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        # Start the TLS encryption
        server.starttls()

        # Log in to the SMTP server
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())

    print("Email sent successfully to", to_address)


# Example usage
if __name__ == "__main__":
    email_subject = "Test Email"
    email_body = "This is a test email sent from Python."
    recipient_address = "rescobar@carhartt.com"

    send_email(email_subject, email_body, recipient_address, pd.DataFrame([1, 2, 3]))
