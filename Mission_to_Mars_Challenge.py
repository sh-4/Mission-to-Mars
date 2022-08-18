# import dependencies
import pandas as pd

# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager

# Set the executable path and initialize Splinter
executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path, headless=False)

### Mars News

# Visit the mars nasa news site
url = 'https://redplanetscience.com'
browser.visit(url)
# Optional delay for loading the page
browser.is_element_present_by_css('div.list_text', wait_time=1)

# set up the HTML parser
html = browser.html
news_soup = soup(html, 'html.parser')
slide_elem = news_soup.select_one('div.list_text')

# assign the title and summary text to variables
slide_elem.find('div', class_='content_title')

# Use the parent element to find the first `a` tag and save it as `news_title`
news_title = slide_elem.find('div', class_='content_title').get_text()

# Use the parent element to find the paragraph text
news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

### Featured Images

# Visit URL
url = 'https://spaceimages-mars.com'
browser.visit(url)

# Find and click the full image button
full_image_elem = browser.find_by_tag('button')[1]
full_image_elem.click()

# Parse the resulting html with soup
html = browser.html
img_soup = soup(html, 'html.parser')

# Find the relative image url
img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

# Use the base URL to create an absolute URL
img_url = f'https://spaceimages-mars.com/{img_url_rel}'

### Mars Facts

df = pd.read_html('https://galaxyfacts-mars.com')[0]

df.columns=['description', 'Mars', 'Earth']
df.set_index('description', inplace=True)

df.to_html()

# # D1: Scrape High-Resolution Mars’ Hemisphere Images and Titles

# ### Hemispheres

# 1. Use browser to visit the URL 
url = 'https://marshemispheres.com/'
browser.visit(url)
# delay for loading the page
browser.is_element_present_by_css('div.list_text', wait_time=1)

# 2. Create a list to hold the images and titles.
hemisphere_image_urls = []

# 3. Write code to retrieve the image urls and titles for each hemisphere.

# scrape main page into Soup
html = browser.html
main_page = soup(html, "html.parser")
    
# parsing variable
hemi_links = main_page.find_all('div', class_="item")

for x in range(len(hemi_links)):
    
     # create an empty dictionary
    hemispheres = {}

    # get each hemi page url
    hemi_url = hemi_links[x].find('a')['href']

    # click on each hemisphere link
    browser.visit(url + hemi_url)
    new_html = browser.html
    next_page = soup(new_html, "html.parser")
    
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

    # add key:values to dictionary
    hemispheres['img_url'] = img_url
    hemispheres['title'] = title

    # add dictionary to list
    hemisphere_image_urls.append(hemispheres)
    
    # navigate back to the beginning to get the next hemisphere image.
    browser.back()
    browser.back()

# 4. Print the list that holds the dictionary of each image url and title.
hemisphere_image_urls

# 5. Quit the browser
browser.quit()