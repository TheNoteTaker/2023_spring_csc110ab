import requests
from bs4 import BeautifulSoup

response = requests.get("https://www.snappedculture.com/")
response.raise_for_status()

site_text = response.text

parsed_text = BeautifulSoup(site_text, 'lxml')
print(parsed_text.prettify())

