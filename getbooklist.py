#!/usr/bin/python3
import sys
import re
from optparse import OptionParser
from bs4 import BeautifulSoup as BS
import urllib3
import certifi

url = "https://www.goodreads.com"
header = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17'


def getpage(inurl):
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    r = http.request('GET', inurl, None, {'User-Agent':header})
    soup = BS(r.data,"lxml")
    return soup

def main(options):
    soup = getpage(url+'/list/tag/'+options.tag)
    print(soup.title.string)
    listoflinks = list()
    booklist = list()
    for links in soup.find_all('a', href=re.compile('/list/show')):
        linkele = links.get('href')
        if not linkele in listoflinks : listoflinks.append(linkele)
    print("BookList with rating > %d NumRating = %d" % (float(options.rating), int(options.numrate)))
    print('Scraping links', end='', flush=True)
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
    booklist.sort(key=lambda x:x.split('==>')[-1].strip())
    print(booklist)

def argparser():
    parser = OptionParser(usage="usage: %prog [-t, --tag | -c, --count]")
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
     options = argparser()
     sys.exit(main(options))


