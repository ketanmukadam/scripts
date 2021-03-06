#!/usr/bin/python3
import sys
import re
import random
from optparse import OptionParser
from bs4 import BeautifulSoup as BS
import urllib3
import certifi
import pickle

url = "https://www.goodreads.com"
header = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17'


def getpage(inurl):
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
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    r = http.request('GET', inurl, None, {'User-Agent':header})
    soup = BS(r.data,"lxml")
    return soup

def fileloadstore(filename, booklist=None, oper=True):
    """
    Load/Store the booklist in pickle database 

    This function will load or store (as per oper argument)
    It will read any existing pickle database and collect the 
    list of books. Any input book list is matched with the 
    read booklist and new items are added in the list and 
    stored back in pickle databse.
    
    Parameters
    ---------
    filename : Name of pickle database 
    booklist : Input any booklist to be stored in pickle database
    oper : True --> Load, False --> Store
    
    Returns
    -------
    tmpbooklist : Return the merged book list from input and read 
    """
    tmpbooklist = list()
    try:
        tmpbooklist = pickle.load(open(filename,'rb'))
    except (OSError, IOError) as e:
        print('%s not found' % filename)
    if not oper: # Store Operation
       if tmpbooklist != booklist:
          for item in booklist:
              if not item in tmpbooklist: tmpbooklist.append(item)  
          pickle.dump(tmpbooklist, open(filename,'wb'))
    return tmpbooklist

def scrapelinks(listoflinks, count):
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
    booklist = list()
    random.shuffle(listoflinks)
    for link in listoflinks:
        s = getpage(url+link)
        print('.', end='', flush=True)
        for booktable in s.find_all('table', class_='tableList js-dataTooltip'):
            bookitems = booktable.find_all('tr', itemtype="http://schema.org/Book")
            for bookitem in bookitems:
                rating = bookitem.find('span', class_='minirating')
                try:
                   avgr, numrate = re.findall('\d+\.\d+|\d+', rating.text.replace(',','')) 
                except ValueError:
                   print("Paring error in ratings -->"+rating.text) 
                if float(avgr) > float(options.rating) and int(numrate.replace(',','')) > int(options.numrate):
                    bookTitle = bookitem.find('a', class_='bookTitle')
                    authorName = bookitem.find('a', class_='authorName')
                    bookelement = bookTitle.text.strip()+' ==> '+authorName.text.strip()
                    if not bookelement in booklist : booklist.append(bookelement)
                    if count == len(booklist) : return booklist

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
    soup = getpage(url+'/list/tag/'+options.tag)
    print(soup.title.string)
    listoflinks = list()
    for links in soup.find_all('a', href=re.compile('/list/show')):
        linkele = links.get('href')
        if not linkele in listoflinks : listoflinks.append(linkele)
    print("BookList with rating > %.2f Minimum Number of Ratings = %d" % (float(options.rating), int(options.numrate)))
    print('Scraping links', end='', flush=True)
    booklist = scrapelinks(listoflinks, int(options.count))
    booklist.sort(key=lambda x:x.split('==>')[-1].strip())
    print(':--> ')
    print(*fileloadstore("booklist.p",booklist,False), sep='\n')

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
        "-t","--tag", dest="tag", help="goodread tag to search", default="investing")
    parser.add_option(
        "-c","--count", dest="count", help="number of book entries to find", default=10)
    parser.add_option(
        "-r","--rating", dest="rating", help="Average rating of book entries to find", default=4.0)
    parser.add_option(
        "-n","--numrate", dest="numrate", help="Number of ratings on book entries", default=10)
    (opts, args) = parser.parse_args(sys.argv)
    return opts

if __name__ == '__main__':
     # Parse the arguments and pass to main
     options = argparser()
     sys.exit(main(options))



