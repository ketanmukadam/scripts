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

def getpage(inurl, tweet_count, fname):
    """
    Get the HTML page from input url 

    This function gets the html page from input url
    It parses using lxml in beautifulsoup and returns
    the soup object

    Parameters
    ---------
    inurl : The url to parse 
    
    Returns
    -------
    soup : beautifulsoup object of parsed url 
    """
    try:
        soup = BS(pickle.load(open(fname, "rb")),"lxml")
    except (OSError, IOError) as e:
        print("Loading webdriver...")
        driver = webdriver.PhantomJS()
        print("Getting url %s..." % inurl)
        driver.get(inurl)
        assert "Twitter" in driver.title

        scroll_count = tweet_count / 15

        while scroll_count:
              print("Scrolling ... [%d]" % scroll_count)
              elemsCount = driver.execute_script("return document.querySelectorAll('.stream-items > li.stream-item').length")
              print("elements [%d]" % elemsCount)
              driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
              try:
                 WebDriverWait(driver, 20).until(
                 lambda x: x.find_element_by_xpath(
                       "//*[contains(@class,'stream-items')]/li[contains(@class,'stream-item')]["+str(elemsCount+1)+"]"))
              except:
                 break
              scroll_count -= 1

        pickle.dump(driver.page_source, open(fname, "wb"))
        soup = BS(driver.page_source,"lxml")
    return soup


def scrapetweets(soup, count):
    """
    Scrape all the links in the input upto count 

    This function will go through all the links in the input list
    It will collect the list of books with rating > input rating 
    and number of ratings > input number of ratings
    The maximum number of books collected is upto input count
    
    Parameters
    ---------
    listoflinks: List containing the links to goodread libraries
    count : Number of books to collect
    
    Returns
    -------
    booklist : Return the list of books collected 
    """
    for tweet in soup.find_all("div",class_="js-tweet-text-container"):
        print(tweet.text)

def main(options):
    """
    Main function of program
    It will scrape the goodreads url based on the input tag
    Collects the list of books from all book libraries (upto max count)
    Stores the book list in the pickle database
    
    Parameters
    ---------
    options: Parsed arguments from command line
    
    Returns
    -------
    None
    """
    soup = getpage("https://www.twitter.com/"+options.user, int(options.count), options.user+".p")
    scrapetweets(soup, int(options.count))
    print(soup.title.string)

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
        "-u","--username", dest="user", help="twitter username", default="contrarianEPS")
    parser.add_option(
        "-c","--count", choices=list(range(15,900,15)), dest="count", help="number of tweets to find", default=15)
    (opts, args) = parser.parse_args(sys.argv)
    return opts

if __name__ == '__main__':
     # Parse the arguments and pass to main
     options = argparser()
     sys.exit(main(options))



