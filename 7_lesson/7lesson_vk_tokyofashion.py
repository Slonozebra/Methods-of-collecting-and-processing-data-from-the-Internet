#Написать программу, которая собирает посты из группы https://vk.com/tokyofashion
#Будьте внимательны к сайту!
#Делайте задержки, не делайте частых запросов!

#1) В программе должен быть ввод, который передается в поисковую строку по постам группы
#2) Соберите данные постов:
#- Дата поста
#- Текст поста
#- Ссылка на пост(полная)
#- Ссылки на изображения(если они есть)
#- Количество лайков, "поделиться" и просмотров поста
#3) Сохраните собранные данные в MongoDB
#4) Скролльте страницу, чтобы получить больше постов(хотя бы 2-3 раза)
#5) (Дополнительно, необязательно) Придумайте как можно скроллить "до конца" до тех пор пока посты не перестанут добавляться

import time
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import urljoin
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
DRIVER_PATH = "chromedriver"

keyword = input('Введите запрос по поиску в постах группы:  ')

url = "https://vk.com/tokyofashion"
driver = webdriver.Chrome(DRIVER_PATH)
wait = WebDriverWait(driver, 10)
options = Options()
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get(url)
driver.refresh()

search_url = driver.find_element_by_class_name('ui_tab_search').get_attribute('href')
driver.get(search_url)
search = driver.find_element_by_id('wall_search')
search.send_keys(keyword)
search.send_keys(Keys.ENTER)
scrollpage = 1
while True:
    time.sleep(2)
    try:
        button = driver.find_element_by_class_name('JoinForm__notNow')
        if button:
            button.click()  #избавляемся от блокировщика
    except Exception as e:
        print(e)
    finally:
        driver.find_element_by_tag_name("html").send_keys(Keys.END)
        scrollpage += 1
        time.sleep(1)
        # ищем конец стены
        wall = driver.find_element_by_id('fw_load_more')
        stopscroll = wall.get_attribute('style')

        if stopscroll == 'display: none;':
            break

posts = driver.find_elements_by_xpath('//div[@id="page_wall_posts"]')


p=0
posts_info = []
for post in posts:
    post_data = {}
    rel_date = post.find_element_by_class_name('rel_date').text
    wall_post_text = post.find_element_by_class_name('wall_post_text').text
    post_link = post.find_element_by_class_name('post_link').get_attribute('href')
    post_photo_links_list = []
    post_photo_links = post.find_elements_by_xpath('.//a[contains(@aria-label,"Original")]')
    for photo in post_photo_links:
        photo_link = photo.get_attribute('aria-label').split()[2]
        post_photo_links_list.append(photo_link)
    post_likes = int(post.find_elements_by_class_name('like_button_count')[0].text)



    post_data['rel_date'] = rel_date
    post_data['wall_post_text'] = wall_post_text
    post_data['post_link'] = post_link
    post_data['post_photo_links_list'] = post_photo_links_list
    post_data['post_likes'] = post_likes


    posts_info.append(post_data)
    p += 1
    print(p)
pprint(posts_info)

db = client['vk_tokyofashion_posts']
collection = db.collection
collection.insert_many(posts_info)
