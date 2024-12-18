from bs4 import BeautifulSoup
import requests
import pandas as pd
from mVariables import team_dictionary, month_list, month_dictionary

def get_months_array(start_url):
    base_url = 'https://www.basketball-reference.com'
    month_link_array = []
    response = requests.get(start_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    season = soup.find('h1').text
    season = season.strip().split(' ')
    season = season[0]
    body = soup.findAll('body')
    months = body[0].findAll('a', href = True)
    for i in months:
        if i.text.lower() in month_list:
            i = (i.text, f'{base_url}{i["hhref"]}')
            month_link_array.append(i)
    page_tocheck_dict = {'Month': [], 'Url': [], 'Index': []}