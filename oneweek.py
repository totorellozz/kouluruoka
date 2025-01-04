import os
import sys
import smtplib
import ssl
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import date
import cred

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)


def fetch_and_send_menu():
    url = "https://aromimenu.cgisaas.fi/EspooAromieMenus/FI/Default/ESPOO/Espoonlahdenkoulujalukio/Restaurant.aspx"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }

    session = requests.Session()

    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    viewstate = soup.find("input", {"id": "__VIEWSTATE"}).get("value")
    viewstate_generator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"}).get("value")
    event_validation = soup.find("input", {"id": "__EVENTVALIDATION"}).get("value")

    #Simulate "SEURAAVA VIIKKO" button click with POST
    post_data = {
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstate_generator,
        '__EVENTVALIDATION': event_validation,
        '__EVENTTARGET': 'ctl00$MainContent$RestaurantDateRangesFilterHeadersDataList$ctl01$RestaurantDateRangesFilterHeadersLinkButton',
        '__EVENTARGUMENT': ''
    }
    post_response = session.post(url, headers=headers, data=post_data)
    soup = BeautifulSoup(post_response.content, 'html.parser')

    #Parse the weekly menu
    menu_details = []

    menu_headers = soup.find_all('div', class_='emenu_tab_panel_header')  # Dates
    menu_panels = soup.find_all('div', class_='emenu_tab_panel_row')  # Menus


    for i, header in enumerate(menu_headers):
        day_span = header.find('span', class_='labeltext')
        menu_day = day_span.get_text(strip=True) if day_span else "Unknown Day"

        panels_for_day = menu_panels[i * 2:(i + 1) * 2]  

        for panel in panels_for_day:
            menu_name_span = panel.find('span', class_='boldtext')
            menu_name = menu_name_span.get_text(strip=True) if menu_name_span else "Unknown Menu"

            menu_details.append(f"{menu_day}\n{menu_name}:")

            dishes = panel.find_all('span', class_='labeltext')
            diets = panel.find_all('span', style="font-weight: 700; font-style: normal;")

            for dish, diet in zip(dishes, diets):
                menu_details.append(f" - {dish.get_text(strip=True)} ({diet.get_text(strip=True)})")

            menu_details.append("")

        # Combine all the details into a single text
    menu_text = "\n".join(menu_details)

    legend_divs = soup.find_all('div', class_='width100percent')

    info = []
    for div in legend_divs:
        code_span = div.find('span', id=lambda x: x and 'CodeOrUniqueCodeSecureLabel' in x)
        name_span = div.find('span', id=lambda x: x and 'NameSecureLabel' in x)
        
        if code_span and name_span:
            code = code_span.get_text(strip=True)
            description = name_span.get_text(strip=True)
            info.append((code, description))
    
    legends_text = "\nInfo:\n"
    for code, description in info:
        legends_text += f"{code}: {description}\n"

    menu_text += legends_text
    print(menu_text)


    #Send email
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = cred.sender_email
    receiver_email = cred.receiver_email
    password = cred.password
    subject = f"Ruokalista {date.today()}"

    body = f"""\
Hei, tässä on viikon ruokalista:\n\n
    {menu_text}
    \n\n
    {url}
    """
    message = MIMEMultipart()
    message["From"] = Header(sender_email, 'utf-8')
    message["To"] = Header(receiver_email, 'utf-8')
    message["Subject"] = Header(subject, 'utf-8')

    message.attach(MIMEText(body, 'plain', 'utf-8'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

fetch_and_send_menu()