# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup, Comment
from pandas import DataFrame

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def scrape_mythic_spoiler(expansion=''):
    link='http://mythicspoiler.com/'+expansion
    print(link)
    nodata=0
    listforpandas=[]
    raw_html=simple_get(link)
    html=BeautifulSoup(raw_html,'html.parser')
    for a in html.find_all('a', {'class':'card'}, href=True):
        cardlink=a['href']
        speciallink=link+cardlink
        cardrawhtml=simple_get(speciallink)
        cardhtml=BeautifulSoup(cardrawhtml,'html.parser')
        cardinfo=list()
        for td in cardhtml.find_all('td'):
            for comment in td.find_all(text=lambda text:isinstance(text, Comment)):
                if comment in ['TYPE','CARD TEXT','P/T','MANA COST']:
                    if td.text.strip() not in cardinfo:
                        cardinfo.append(td.text.strip())
        if len(cardinfo)==['']:
            nodata=nodata+1
        cardinfo.append(cardlink)
        listforpandas.append(cardinfo)
    for i in listforpandas:
        try:
            i.append(i[4].split('/')[0])
        except:
            pass
        try:
            i.append(i[4].split('/')[1])
        except:
            i.append('')
    print('{} cards with no data'.format(nodata))
    return listforpandas
data=scrape_mythic_spoiler()
carddf=DataFrame(data)
carddf.columns=['Name','Mana Cost', 'Type','Effect','P/T','link','power','toughness']
carddf.to_csv('Ikoria.csv')