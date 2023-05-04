import os
import sys
import requests  # Installed
import urllib.parse
import json
from pathlib import Path
from selenium import webdriver  # Installed
from selenium.webdriver.chrome.options import Options  # Installed
from bs4 import BeautifulSoup as Soup  # Installed

# Setup Selenium Webdriver
options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

mdBook_url = sys.argv[1]  # URL to mdBook website
post_queries_json = "https://raw.githubusercontent.com/"+sys.argv[2]+"/"+sys.argv[3]+"/queries.json"  # raw URL to queries.json Ideally on a POST branch
reprocess_cache = False
if len(sys.argv) > 4:
    reprocess_cache = sys.argv[4]  # to define if triggered by site deployment


class Query(dict):
    def __init__(self, query, cached=None, empty=None):
        if empty is None:
            empty = False
        if cached is None:
            cached = False
        dict.__init__(self, query=query, cached=cached, empty=empty)
        self.cached = cached
        self.query = query
        self.empty = empty


class SearchResult(dict):
    def __init__(self, title, href, paragraph_preview):
        dict.__init__(self, title=title, href=href, paragraph_preview=paragraph_preview)


def url_string(string):
    return urllib.parse.quote(string, '/#')


def get_html(url):
    driver.get(url)
    return driver.page_source


def get_processed_results(query_url):
    html_item = Soup(get_html(query_url), 'html.parser')
    results_ul = html_item.find("ul", id="searchresults")
    results = results_ul.find_all('li')
    processed_results = []
    for result in results:
        title = result.a.get_text()
        result_href = query_url[0:query_url.find("?")] + url_string(result.a['href'])
        paragraph_preview = result.span.get_text()
        process_result = SearchResult(title, result_href, paragraph_preview)
        processed_results.append(process_result)
    return processed_results


def generate_query_json(query):
    print("Processing Search Query: " + query)
    query_path = sys.argv[0].replace("generate_index_JSON.py", "out/query/" + query)
    p = Path(os.path.dirname(query_path))
    p.mkdir(exist_ok=True)
    with open(query_path, "w") as outfile:
        query_url = mdBook_url + "?search=" + url_string(query)
        results = get_processed_results(query_url)
        outfile.write(json.dumps(results, indent=2))
        print("Done processing Search Query: " + query)
        return len(results) == 0


def process_queries_json():
    print("Start Processing queries.json")
    queries = requests.get(post_queries_json).json()
    processed_queries = []
    for query in queries:
        query_read = Query(**query)
        result = True
        if not query_read.cached or reprocess_cache:
            result = generate_query_json(query_read.query)
        processed_queries.append(Query(query_read.query, True, result))
    print("Done processing queries.json")
    return json.dumps(processed_queries, indent=2)


def start():
    print("Start Static API generation")
    if reprocess_cache:
        print("Reprocessing Cache Mode Active")
    queries = sys.argv[0].replace("generate_index_JSON.py", "out/queries.json")
    p = Path(os.path.dirname(queries))
    p.mkdir(exist_ok=True)
    with open(queries, "w") as outfile:
        outfile.write(process_queries_json())
    driver.close()
    print("Exit")


start()
