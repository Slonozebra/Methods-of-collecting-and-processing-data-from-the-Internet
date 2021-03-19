#1) Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex.news
#Для парсинга использовать xpath. Структура данных должна содержать:
#- название источника,
#- наименование новости,
#- ссылку на новость,
#- дата публикации


from lxml import html
from pprint import pprint
import requests
from pymongo import MongoClient

main_link_mail = 'https://news.mail.ru'
main_link_lenta = 'https://lenta.ru'
main_link_yandex = 'https://yandex.ru/news'


def get_dom(link):
    header = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
    response = requests.get(link, headers=header)
    dom = html.fromstring(response.text)
    return dom

def list_len(list):
    try:
        el = list[0].replace('\xa0', ' ')
        return el
    except:
        pass

def link_constr(main_link, link):
    if 'https://' not in link:
        link = main_link + link
    else:
        link
    return link

def add_collection(news_dict, collection):
    for new in news_dict:
        count = 0
        if collection.count_documents({'title': new['title']}) == 0:
            collection.insert_one(new)
            count += 1
    print(f'В коллекцию {collection.name} добавлено {count} документов. Всего документов в коллекции {collection.count_documents({})}')


# lenta.ru

dom_lenta = get_dom(main_link_lenta)

section = dom_lenta.xpath(
    "//section[@class='row b-top7-for-main js-top-seven']//div[@class='item'] | //section[@class='row b-top7-for-main js-top-seven']//div[@class='first-item']")

lenta_news = []

for new in section:
    lenta_new = {}
    title = list_len(new.xpath("./a/text() | ./h2/a/text()"))

    link = list_len(new.xpath(".//@href | ./h2//@href"))
    link = link_constr(main_link_lenta, link)

    date = list_len(new.xpath(".//time/@datetime | .//time/@datetime"))
    source = main_link_lenta

    lenta_new['source'] = source
    lenta_new['title'] = title
    lenta_new['link'] = link
    lenta_new['date'] = date

    lenta_news.append(lenta_new)

pprint(lenta_news[0])


#mail.ru

dom_mail = get_dom(main_link_mail)

section = dom_mail.xpath("//div[contains(@data-counter-id, '20268335')]//a[contains(@class, photo)]")

mail_news = []

for new in section:
    mail_new = {}

    link = list_len(new.xpath(".//@href"))
    link = link_constr(main_link_mail, link)

    temp_dom = get_dom(link)

    title = list_len(temp_dom.xpath("//h1/text()"))
    date = list_len(temp_dom.xpath("//span[@class = 'note__text breadcrumbs__text js-ago']/@datetime"))
    source = list_len(temp_dom.xpath("//a[@class = 'link color_gray breadcrumbs__link']//span/text()"))

    mail_new['source'] = source
    mail_new['title'] = title
    mail_new['link'] = link
    mail_new['date'] = date

    mail_news.append(mail_new)

pprint(mail_news[0])

#yandex.ru

dom_yandex = get_dom(main_link_yandex)

section = dom_yandex.xpath("//div[@class = 'mg-grid__row mg-grid__row_gap_8 news-top-flexible-stories news-app__top']")

yandex_news = []

for new in section:
    yandex_new = {}

    title = list_len(new.xpath(".//h2/text()"))
    link = list_len(new.xpath(".//a/@href"))
    link = link_constr(main_link_yandex, link)

    date = list_len(new.xpath(".//span[@class = 'mg-card-source__time']/text()"))
    source = list_len(new.xpath(".//span[@class = 'mg-card-source__source']/a/text()"))

    yandex_new['source'] = source
    yandex_new['title'] = title
    yandex_new['link'] = link
    yandex_new['date'] = date

    yandex_news.append(yandex_new)

pprint(yandex_news[0])

#2) Сложить все новости в БД(MongoDB)
client = MongoClient('127.0.0.1', 27017)
db = client['news_database']
news_lenta = db.news_lenta
news_yandex = db.news_yandex
news_mail = db.news_mail
add_collection(lenta_news, news_lenta)
add_collection(mail_news, news_mail)
add_collection(yandex_news, news_yandex)