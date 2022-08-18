# import dependencies
import datetime as dt
import pandas as pd

# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager

# function to initialize browser, create data dictionary, end webdriver and return scraped data
def scrape_all():
    # Initiate headless driver for deployment through splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
        # headless changed to true since the scraping does not need to be seen in-action
    
    # set variables
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": mars_hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

# scrape mars news function
def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # set up the HTML parser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None

    # end the function
    return news_title, news_p

# ## JPL Space Images Featured Image

# scrape featured images function
def featured_image(browser):

    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    # end the function
    return img_url

# ## Mars Facts

# scrape mars facts table function
def mars_facts():

    # try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]
    
    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # end the function, convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table background-color:#000000")

def mars_hemispheres(browser):

    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    # delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Retrieve the image urls and titles for each hemisphere.

    # scrape main page into Soup
    html = browser.html
    main_page = soup(html, "html.parser")
        
    # parsing variable
    hemi_links = main_page.find_all('div', class_="item")

    for x in range(len(hemi_links)):
        
        # create an empty dictionary
        hemisphere = {}

        # get each hemi page url
        hemi_url = hemi_links[x].find('a')['href']

        # click on each hemisphere link
        browser.visit(url + hemi_url)
        new_html = browser.html
        next_page = soup(new_html, "html.parser")
        
        # try/except for error handling
        try:    
            # retrieve the title for the hemisphere image
            title_header = next_page.find_all('h2', class_="title")
            title = title_header[0].text
            
            # navigate to the full-resolution image
            sample = next_page.find_all('div', class_="downloads")  
            img = sample[0]('li')[0]('a')[0].get('href')
            browser.visit(url + img)
            new_html = browser.html
            next_page = soup(new_html, "html.parser")
            
            # retrieve the full-resolution image URL string
            img_url = next_page.find('img').get('src')
        
        except AttributeError:
            return None

        # add key:values to dictionary
        hemisphere['img_url'] = img_url
        hemisphere['title'] = title

        # add dictionary to list
        hemisphere_image_urls.append(hemisphere)
        
        # navigate back to the beginning to get the next hemisphere image.
        browser.back()
        browser.back()

    return hemisphere_image_urls

# tell Flask this script is complete and ready
if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())