import requests
from bs4 import BeautifulSoup

url = "https://aromimenu.cgisaas.fi/EspooAromieMenus/FI/Default/ESPOO/Espoonlahdenkoulujalukio/Restaurant.aspx"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
}

session = requests.Session()

# Initial GET request
response = session.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

menu = soup.find_all('div', class_='emenu_tab_panel_row') 
for item in menu:
    print(item.get_text(strip=True))

