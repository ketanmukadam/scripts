Simple Python Scripts 
---------------------

This repository contains python scripts for automating various tasks. 

Here is the summary of all scripts
   * `getbooklist.py` - Get a filtered list of book names from goodreads website
	 
			Usage: getbooklist.py [options]
			Options:
			-h, --help                    show this help message and exit
			-t TAG, --tag=TAG             goodread tag to search
			-c COUNT, --count=COUNT       number of book entries to find
			-r RATING, --rating=RATING    Average rating of book entries to find
			-n NUMRATE, --numrate=NUMRATE Number of ratings on book entries
						 
   * `getuserbookshelf.py` - Get list of books in the shelf of goodreads user
	 
			Usage: getuserbookshelf.py [options]
			Options:
			-h, --help                  show this help message and exit
			-u USER, --username=USER    goodread username
			-c COUNT, --count=COUNT     number of books to scrape
			-s SKIP, --skip=SKIP        number of books to skip
	
   * `gettwitterfeed.py` - Scrape the latest feeds from a twitter user
	 
			Usage: gettwitterfeed.py [options]
			Options:
			-h, --help               show this help message and exit
			-u USER, --username=USER twitter username
			-c COUNT, --count=COUNT  number of tweets to find
				
   * `googlequery.py` - Search for a company url on moneycontrol website 
			
			Usage: googlequery.py [options]
			Options:
			-h, --help                           show this help message and exit
			-s SEARCHTEXT, --srchtxt=SEARCHTEXT  text for search

## License

See the [LICENSE](LICENSE.md) file for license rights and limitations.
