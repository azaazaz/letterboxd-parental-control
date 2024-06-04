from selenium import webdriver
from bs4 import BeautifulSoup
import time
from imdb import IMDb # TODO own title finder
import xlsxwriter

username = input("username: ")
# movie titles from user's letterboxd
titles = []
# urls of parental guide page of according movies
urls = []

# returns a list of titles
def watchlist(username):
    cService = webdriver.ChromeService(executable_path='/usr/bin/chromedriver')
    driver = webdriver.Chrome(service = cService)


    thing_url_original = f"https://letterboxd.com/{username}/watchlist/"
    thing_url = thing_url_original
    
    counter = 1 # going through pages

    while True:
        driver.get(thing_url)
        time.sleep (2)
        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')

        if counter == 1:
            try:
                li_tags = soup.find('div', class_='paginate-pages').find_all('li')

                # Get the text from the last li element
                stopper = li_tags[-1].get_text()
                # how many total pages this user has
                print("\n stopper is", stopper)
            except:
                stopper = 0
                print("\n stopper is", stopper)

        new_titles = soup.find_all('span', class_='frame-title')
        titles.extend (new_titles)

        counter += 1
        if counter > int(stopper):
            break

        thing_url = thing_url_original + f"page/{counter}/"

    driver.close()

    for i in range (0,len(titles)):
        titles[i] = titles[i].text

    return titles


def parental_url (movie_titles):
    ia = IMDb()

    for movie in movie_titles:
    
        # TODO find id of the movie
        imdb_id = ia.search_movie(movie)[0].movieID
        # imdb_id = movies[0].movieID

        parental_url = f"https://www.imdb.com/title/tt{imdb_id}/parentalguide"
        urls.append(parental_url)
        print(parental_url)
    return urls
        
def nudity(urls):
    cService = webdriver.ChromeService(executable_path='/usr/bin/chromedriver')
    driver = webdriver.Chrome(service = cService)

    workbook = xlsxwriter.Workbook('nudity.xlsx')
    worksheet = workbook.add_worksheet()


    # for each movie from watchlist
    for i in range (0, len(urls)):

        driver.get(urls[i])
        time.sleep (2)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        movie_name = soup.find('div',{"class": "subpage_title_block__right-column"}).find('a').text

        print(movie_name)

        worksheet.write_string(i, 0, movie_name) 

        nudity_section = soup.find('section',{"id": "advisory-nudity"})

        li_tags = nudity_section.find_all('li', class_='ipl-zebra-list__item')

        if (len(li_tags) == 0):
            worksheet.write_string(i, 1, "nothing to worry about") 
            continue

        for j in range (0, len(li_tags)):
            # there was Edit at the ead of each str which didnt let to strip normalno
            text = li_tags[j].text[:-10].strip()
            worksheet.write_string(i, j+1, text) 
        
    workbook.close()


    driver.close()


nudity(parental_url(watchlist(username)))