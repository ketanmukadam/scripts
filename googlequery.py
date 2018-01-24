#!/usr/bin/python3

import sys
from optparse import OptionParser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException 


def query_google(options):
     if not options.searchtext : return None
     browser = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
     browser.get("https://www.google.co.in/search?q="+"moneycontrol "+options.searchtext)
     #assert options.searchtext in browser.title
     browser.implicitly_wait(50)
     soup = BeautifulSoup(browser.page_source ,"html.parser")
     links = []
     for item in soup.find_all('h3', attrs={'class' : 'r'}):
             links.append(item.a['href'][7:]) # [7:] strips the /url?q= prefix
     return ([links[0] if links else None]) 

def argparser():
    """
    Option parsing of command line

    It will add the required arguments to OptionParser module
    Collects and parse the arguments
    
    Parameters
    ---------
    None 
    
    Returns
    -------
    opts: Parsed arguments (or their defaults) returned in opts
    """
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option(
        "-s","--srchtxt", dest="searchtext", help="text for search", default="Mayur Uniquoter")
    (opts, args) = parser.parse_args(sys.argv)
    return opts

if __name__ == '__main__':
     # Parse the arguments and pass to main
     options = argparser()
     sys.exit(print(query_google(options)))


