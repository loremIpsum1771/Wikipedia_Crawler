# Wikipedia_Crawler
This repo features a coded example of the [getting to philosophy phenomenon](https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy) which is essentially that if you click on the first first link on the main body of a wikipedia article that is not within parenthesis or italicized, repeating this process will often eventually lead to the philosophy page.

The class in the file `wiki_crawler.py` selects a fixed number of random article (based on the number passed in) and starting from those links, navigates along the path of links until the philosophy page is reached. Each path length is recorded in a list and then the entire list of lengths is graphed using the matplotlib with the graph being fitted with a normal distribution.

## Quickstart/Setup:

1. Clone the repository/ Download the .zip file
2. Open a terminal window
3. Execute the command: `cd Wikipedia_Crawler`
3. Install the package Tkinter (required for matplotlib) by executing the command: `sudo apt-get install python3-tk`
4. Install the rest of the dependencies with:
```
   pip install -r requirements.txt
```
5. Run the web scraper using: `python wiki_crawler.py`
