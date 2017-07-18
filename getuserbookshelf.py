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

def scrapebookisbn(driver, bookname):
    """
    Scrape the ISBN number of the bookname 

    This function will search the bookname on goodreads and  
    scrape the ISBN number
    
    Parameters
    ---------
    bookname : Name of book to search
    
    Returns
    -------
    None 
    """
    print("Searching ISBN for %s" % bookname)
    driver.get("https://www.goodreads.com/")
    try:
       WebDriverWait(driver, 3).until(
             EC.presence_of_element_located((By.ID, "sitesearch_field"))
       )
       driver.find_element_by_id("sitesearch_field").send_keys(bookname)
       driver.find_element_by_id("sitesearch_field").send_keys(Keys.ENTER)
       WebDriverWait(driver, 3).until(
             EC.presence_of_element_located((By.LINK_TEXT, bookname))
       )
       driver.find_element_by_link_text(bookname).click()
       WebDriverWait(driver, 5).until(
             EC.presence_of_element_located((By.ID, "bookDataBox"))
       )
    except (NoSuchElementException, TimeoutException) :
       print("No element found %s" % bookname)
       return " "  
    soup = BS(driver.page_source,"lxml")
    elements = soup.findAll("div", {"class" : "clearFloats"})
    for isbntags in elements:
        isbnval = isbntags.findAll("div")
        if isbnval[0].text.strip() == "ISBN": break
        if isbnval[0].text.strip() == "ISBN13": break
        if isbnval[0].text.strip() == "ASIN": break
    return isbnval[1].text.split()[0]

def scrapebookshelf(soup, skip_count, get_count):
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
    driver = webdriver.PhantomJS()
    for tableentry in soup.find_all("tbody",id="booksBody"):
        rows = tableentry.find_all("tr")
        for row in rows:
            if skip_count:
               skip_count -= 1
               continue
            if not get_count: break
            titlecols = row.find_all("td", attrs={"class" : "field title"})
            authorcols = row.find_all("td", attrs={"class" : "field author"})
            titlecols = [ele.find("div",attrs={"class" : "value"}).text.strip() for ele in titlecols if ele]
            authorcols = [ele.find("div",attrs={"class" : "value"}).text.strip() for ele in authorcols if ele]
            for t, a in zip(titlecols, authorcols):
                isbn = scrapebookisbn(driver,t) 
                booklist.append(t+"  "+a+"  "+isbn)
            get_count -= 1
    print(booklist)
    try: 
       ftxt = open('booklist.txt','w')
       for b in booklist:
           ftxt.write("%s\n" % b)
    except (OSError, IOError) as e:
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
    scrapebookshelf(getpage("https://www.goodreads.com/review/list/"+options.user+"?shelf=%23ALL%23&view=table", options.user+".p"), int(options.skip), int(options.count))

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
    parser.add_option(
        "-c","--count", dest="count", help="number of books to scrape", default="100")
    parser.add_option(
        "-s","--skip", dest="skip", help="number of books to skip", default="0")
    (opts, args) = parser.parse_args(sys.argv)
    return opts

if __name__ == '__main__':
     # Parse the arguments and pass to main
     options = argparser()
     sys.exit(main(options))



