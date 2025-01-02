import os
import sys

# Add the script directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

import smtplib, ssl
import cred
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import date


def fetch_and_send_menu():
    # Step 1: Make the initial request to get the current page's hidden fields
    url = "https://aromimenu.cgisaas.fi/EspooAromieMenus/FI/Default/ESPOO/Espoonlahdenkoulujalukio/Restaurant.aspx"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }

    # Start a session to persist cookies
    session = requests.Session()
    menu_details = []
    data = date.today()

    # Initial GET request
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    menu_panels = soup.find_all('div', class_='emenu_tab_panel_row')  # Adjust the selector based on the actual structure
    for panel in menu_panels:
        menu_name = panel.find('span', class_='boldtext').get_text(strip=True)
        menu_details.append(f"{menu_name}:")

        # Extract all the dish names and their diet information
        dishes = panel.find_all('span', class_='labeltext')
        diets = panel.find_all('span', style="font-weight: 700; font-style: normal;")

        for dish, diet in zip(dishes, diets):
            menu_details.append(f" - {dish.get_text(strip=True)} ({diet.get_text(strip=True)})")

        menu_details.append("")

    menu_text = "\n".join(menu_details)
    print(menu_text, '\n', url)

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "tommi.mosconi@gmail.com"  # Enter your address
    receiver_email = "tommi.mosconi@gmail.com"  # Enter receiver address
    password = cred.password
    subject = f"Ruokalista {data}"

    body = f"""\
Hei, tässä on ruokalista:\n\n
    {menu_text}
    \n\n
    {url}
    """
    message = MIMEMultipart()
    message["From"] = Header(sender_email, 'utf-8')
    message["To"] = Header(receiver_email, 'utf-8')
    message["Subject"] = Header(subject, 'utf-8')

    # Attach the body with UTF-8 encoding
    message.attach(MIMEText(body, 'plain', 'utf-8'))

    # Setup the SSL context
    context = ssl.create_default_context()

    # Send the email
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

fetch_and_send_menu()