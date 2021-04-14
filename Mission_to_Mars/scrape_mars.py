# import dependancies
from splinter import Browser
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd 
import pymongo 
import requests 

def init_browser():
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()

    #NASA Mars News

    url1 = "https://mars.nasa.gov/news"
    browser.visit(url1)
    time.sleep(5)
    html = browser.html
    soup = bs(html, 'html.parser')

    #scrape site to collect latest title
    news_title = soup.find_all(class_ = "content_title")
    top_news_title = news_title[1]
    #scrape site to collect the paragraph text
    news_p = soup.find_all(class_ = "article_teaser_body")
    top_news_p = news_p[0]

    #JSL Mars Space Image

    url2 = 'https://www.jpl.nasa.gov/images?search=&category=Mars'
    browser.visit(url2)
    time.sleep(5)
    html2 = browser.html
    soup = bs(html2, 'html.parser')

    #find the image source
    feature_image_url = soup.find(class_ = "BaseImage")['src']

    #visit the Mars facts url

    url3 = 'https://space-facts.com/mars/'
    browser.visit(url3)
    time.sleep(5)
    html3 = browser.html
    soup = bs(html3, 'html.parser')

    facts = pd.read_html(url3)
    facts_df = facts[0]
    mars_facts = facts_df.rename(columns={0 : "Features", 1 : "Value"}).set_index(["Features"])
    mars_table = mars_facts.to_html()
    mars_table.replace('\n','')

    #visit the USGS astrogeology url
    url4 = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url4)
    time.sleep(5)
    html4 = browser.html
    soup = bs(html4, 'html.parser')

    products = soup.find('div', class_ = 'collapsible results')
    hemispheres=products.find_all('a')

    hemisphere_image_urls = []

    for hemisphere in hemispheres:
        if hemisphere.h3:
            title=hemisphere.h3.text
            link=hemisphere["href"]
            main_url="https://astrogeology.usgs.gov/"
            next_url=main_url+link
            browser.visit(next_url)
            time.sleep(5)
            html = browser.html
            soup = bs(html, 'html.parser')
            hemisphere2=soup.find("div",class_= "downloads")
            img=hemisphere2.ul.a["href"]
            hemisphere_dict={}
            hemisphere_dict["Title"]=title
            hemisphere_dict["Image_URL"]=img
            hemisphere_image_urls.append(hemisphere_dict)
            browser.back()

    Mars={
        "Mars_news_title": top_news_title,
        "Mars_news_p": top_news_p,
        "Featured_mars_image": feature_image_url,
        "Mars_facts": mars_table,
        "Mars_hemispheres": hemisphere_image_urls
    }
    browser.quit()

    return Mars