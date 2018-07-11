import sys
import json
from urlparse import urljoin

import requests
from lxml.html import fromstring
from bs4 import BeautifulSoup,NavigableString, Tag
import matplotlib.pyplot as plt
import scipy
import scipy.stats

reload(sys)
sys.setdefaultencoding('utf-8')


class Crawler:
    """ Class used to crawl wikipedia pages starting from a random article."""
    def __init__(self, numPages):
        self.base_url = "https://en.wikipedia.org"
        self.NUM_PAGES_TO_CRAWL = numPages
    def get_valid_link(self, curr_response):
        """Takes an html response and returns the first link in the main body of the article."""
        curr_root = BeautifulSoup(curr_response.text,"lxml")
        first = curr_root.select_one("#mw-content-text > div") # locate main body
        if not first:
            return None
        par = first.find_all("p",recursive = False,limit = 10)
        heading = curr_root.select_one("#firstHeading").text
        heading = reformat_string('(',heading)
        first_paragraph_found = False
        head_tokens = tokenize(heading)

        # Find which paragraph has the first link
        i = 0
        for i in range(len(par)):
            if par[i].b is not None:
                bold = ""
                for string in par[i].find_all("b"):
                    bold += " " + string.text
                bold = reformat_string('(', bold)
                bold_tokens = tokenize(bold)
                heading_match = check_name_match(head_tokens,bold_tokens)
                if heading_match:
                    first_paragraph_found = True
                if heading_match and par[i].a:
                    break
            if par[i].a is not None:
                anchor = par[i].a.text
                if anchor:
                    anchor = reformat_string('(', anchor)
                    a_tokens = tokenize(anchor)
                    heading_match = check_name_match(head_tokens,a_tokens)
                    if heading_match:
                        break
            if first_paragraph_found and par[i].a:
                break   
            i += 1

        # if none of the paragraphs have a link and article contains only a list
        if i >= len(par)-1 and first_paragraph_found:
            u_list = first.find_all('ul')
            try:
                return u_list[0].li.a['href']
            except (IndexError, AttributeError,TypeError):
                return None
        elif i >= len(par)-1:# Reached article with no main body
            return None

        main_body_idx = i
        stack = []
        # Find the first link before or after parentheses 
        for child in par[main_body_idx].children:
            if isinstance(child,NavigableString):
                if "(" in child:
                    stack.append("(")
                if ")" in child:
                    try:
                        stack.pop()
                    except IndexError: # html malformed
                        return None

            if isinstance(child, Tag) and child.name == "a" and not stack:
                link = child['href']        
                link = reformat_string('#',link)
                try:
                    return str(link)
                except KeyError: # Reached article with no main body
                    return None

    def crawl_to_philosophy(self, start_url,session):
        """Follow the path of each url until the philosophy page is reached and return the path."""
        link_path = []
        # Get first link
        try:
            init_response = session.get(start_url)
        except requests.exceptions.RequestException as e: # bad link
            return None

        init_link = self.get_valid_link(init_response)
        if not init_link:
            return None
        link_path.append(urljoin(self.base_url, init_link))

        # Follow path of links until the philosophy page is reached
        i = 0
        while True:
            if "philosophy" in  link_path[i].lower():
                break
            try:
                curr_response = session.get(link_path[i])
            except requests.exceptions.RequestException as e: # bad link
                return None 

            curr_link = self.get_valid_link(curr_response)
            if not curr_link or "redlink" in curr_link:
                return None
            new_link = urljoin(self.base_url, curr_link)
            for i in range(len(link_path)):
                if new_link in link_path[i] : # loop found
                    return None
            print "new_link: " + new_link
            link_path.append(new_link)
            i += 1
        return link_path

    def find_paths_to_philosophy(self,url):
        """Find paths starting from NUM_PAGES_TO_CRAWL links."""
        i = 0
        crawl_list = []
        with requests.Session() as s:
            while i < self.NUM_PAGES_TO_CRAWL:
                path = self.crawl_to_philosophy(url,s)
                if path is not None:
                    crawl_list.append(len(path))
                    i += 1
            plot_lengths(crawl_list)


def plot_lengths(lens):
    """Plot the distribution of path lengths."""
    freq = {}
    max_len = 0

    for length in lens:
        max_len = max(length,max_len)
        if length in freq:
            freq[length] += 1
        else:
            freq[length] = 1
    max_freq = max(freq.values())
    bins = range(0, max_len + 1, 2)
    plt.hist(lens,bins,histtype = 'bar',rwidth = 0.8)
    plt.xlabel('x')
    plt.ylabel('Path Lengths')
    plt.title('Distribution of path lengths')
    dist_names = ['gamma', 'beta', 'rayleigh', 'norm', 'pareto']

    for dist_name in dist_names:
        dist = getattr(scipy.stats, dist_name)
        param = dist.fit(lens)
        pdf_fitted = dist.pdf(bins, *param[:-2], loc=param[-2], scale=param[-1]) * len(lens)
        plt.plot(bins,pdf_fitted, label=dist_name)
        plt.xlim(0,max_len)
        plt.ylim(0,max_freq)
    plt.legend(loc='upper right')
    plt.show()


# Utility functions used by Crawler class

def reformat_string(char, word):
    """Remove passed in char from a string and convert its characters to lowercase."""
    word = word.lower()
    char_idx = word.find(char)
    if char_idx != -1:
        return word[:char_idx]
    return word

def check_name_match(heading, string):
    """Determine whether or not any part of the article heading is in the string and vice versa."""
    for i in range(len(string)):
        for j in range(len(heading)):
            if heading[j] in string[i] or string[i] in heading[j]:
                return True
    return False

def tokenize(word):
    """Split the passed in 'word' on space characters and return a list of tokens."""
    tokens = []
    curr_word = ""
    for i in range(len(word)):
        if word[i] == " " and i == len(word)-1:
            tokens.append(word.strip(" "))
            return tokens
        curr_word += word[i]
        if word[i] == " " :
            tokens.append(curr_word)    
            curr_word = ""
            i+=1
        if i == len(word)-1:
            tokens.append(curr_word)    
            return tokens


if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Special:Random"
    numPages = 1
    crawler = Crawler(numPages)
    crawler.find_paths_to_philosophy(url)
