import requests
from bs4 import BeautifulSoup
import re

def scrape_flipkart_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    main_div = soup.find('div', class_='_1UhVsV')
    details_divs = main_div.find_all('div', class_='_3k-BhJ')

    product_details = []
    price=soup.find('div',class_='_30jeq3 _16Jk6d').text.strip()
    product_details.append(f"Price : {price}")
    for div in details_divs:
        category = div.find('div', class_='flxcaE').text.strip()
        table = div.find('table', class_='_14cfVK')
        product_details.append(category)
        for row in table.find_all('tr', class_='_1s_Smc row'):
            key = row.find('td', class_='_1hKmbr col col-3-12').text.strip()
            value = row.find('td', class_='URwL2w col col-9-12').text.strip()
            product_details.append(f" {key}: {value}")

    return '\n'.join(product_details)


def extract_info(string):
    pattern = r'(https?://\S+)'
    match = re.search(pattern, string)
    if match:
        return scrape_flipkart_details(match.group(1))
    else:
        return None
