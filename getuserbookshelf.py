#!/usr/bin/python3
import sys
import re
import time
import pickle
from optparse import OptionParser
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException 

def getpage(inurl, fname):
    """
    Get the HTML page from input twitter url 

    This function gets the twitter feed page from the url 
    It parses using lxml in beautifulsoup and returns
    the soup object

    Parameters
    ---------
    inurl : The url to parse 
    tweet_count : Number of tweets to get. Assuming 15 tweets 
                  per page, it will scroll the twitter feed
    fname : pickle filename to store/load the tweet page

    Returns
    -------
    soup : beautifulsoup object of parsed url 
    """
    try:
        print("Trying to read pickle database %s" % fname)
        soup = BS(pickle.load(open(fname, "rb")),"lxml")
    except (OSError, IOError) as e:
        print("Loading webdriver...")
        driver = webdriver.PhantomJS()
        print("Getting url %s..." % inurl)
        driver.get(inurl)
        assert "bookshelf" in driver.title

        lastHeight = driver.execute_script("return document.body.scrollHeight")
        while True:
              print("Scrolling lastHeight [%d]" % lastHeight)
              driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
              time.sleep(3)
              newHeight = driver.execute_script("return document.body.scrollHeight")
              if newHeight == lastHeight:
                 break
              lastHeight = newHeight

        print("Dumping source in pickle database")
        pickle.dump(driver.page_source, open(fname, "wb"))
        soup = BS(driver.page_source,"lxml")
    return soup


def scrapebookshelf(soup):
    """
    Scrape all the books in the bookshelf 

    This function will go through the soup object and scrape 
    all the books in the user's bookshelf 
    
    Parameters
    ---------
    soup : soup object of the twitter feed page 
    count : Number of books to display 
    
    Returns
    -------
    None 
    """
    booklist = list()
    for tableentry in soup.find_all("tbody",id="booksBody"):
        rows = tableentry.find_all("tr")
        for row in rows:
            titlecols = row.find_all("td", attrs={"class" : "field title"})
            authorcols = row.find_all("td", attrs={"class" : "field author"})
            titlecols = [ele.find("div",attrs={"class" : "value"}).text.strip() for ele in titlecols if ele]
            authorcols = [ele.find("div",attrs={"class" : "value"}).text.strip() for ele in authorcols if ele]
            for t, a in zip(titlecols, authorcols):
                booklist.append(t+"-"+a)
    print(*booklist, sep='\n') 
    print("Found %d books in bookshelf" % len(booklist)) 

def main(options):
    """
    Main function of program
    It will scrape the book list on the input username 
    
    Parameters
    ---------
    options: Parsed arguments from command line
    
    Returns
    -------
    None
    """
    scrapebookshelf(getpage("https://www.goodreads.com/review/list/"+options.user+"?shelf=%23ALL%23&view=table", options.user+".p"))

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
        "-u","--username", dest="user", help="goodread username", default="44743670-sanjay-bakshi")
    (opts, args) = parser.parse_args(sys.argv)
    return opts

if __name__ == '__main__':
     # Parse the arguments and pass to main
     options = argparser()
     sys.exit(main(options))



