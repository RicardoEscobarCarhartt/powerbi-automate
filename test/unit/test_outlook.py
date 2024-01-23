"""This module is used to test the outlook module to send emails using
outlook"""
import os

import win32com.client as client
from dotenv import load_dotenv
import pandas as pd


# Load the environment variables from the .env file
load_dotenv()


def send_email(
    subject,
    body,
    to_address,
    database_dataframe: pd.DataFrame,
    powerbi_dataframe: pd.DataFrame,
):
    """This function is used to send emails using outlook"""
    from_address = os.getenv("OUTLOOK_SENDER_EMAIL")

    # Convert the Pandas DataFrame to an HTML table
    database_table_html = database_dataframe.to_html(index=False)
    powerbi_table_html = powerbi_dataframe.to_html(index=False)

    # Create the html email body with the table
    html_body = f"""<h3>There are differences in the dataset</h3>\n\n
    {body}\n\n
    <h2>Dabatase</h2>{database_table_html}\n\n
    <h2>PowerBI</h2>{powerbi_table_html}"""

    outlook = client.Dispatch("Outlook.Application")
    message = outlook.CreateItem(0)
    message.Display()
    message.To = to_address
    message.Subject = subject
    message.Body = body
    message.HTMLBody = html_body
    message.Send()

    print("Email sent successfully to", to_address)


if __name__ == "__main__":
    email_subject = "Test Email"
    email_body = "This is a test email sent from Python."
    recipient_address = "rescobar@carhartt.com"
    database_dataframe = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    powerbi_dataframe = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 7]})

    send_email(email_subject, email_body, recipient_address, database_dataframe, powerbi_dataframe)
