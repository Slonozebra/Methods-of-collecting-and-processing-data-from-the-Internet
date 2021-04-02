#Парсинг Instagram
#1) Написать приложение, которое будет проходиться по указанному списку(делать через ввод input) двух и/или более пользователей и собирать данные об их подписчиках и подписках.
#2) По каждому пользователю, который является подписчиком или на которого подписан исследуемый объект нужно извлечь имя, id, фото (остальные данные по желанию). Фото можно дополнительно скачать(необязательно).
#3) Собранные данные необходимо сложить в базу данных. Структуру данных нужно заранее продумать(!), чтобы:
#4) Написать функцию, которая будет делать запрос к базе, который вернет список подписчиков только указанного пользователя
#5) Написать функцию, которая будет делать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagramparser.spiders.instagram import InstagramSpider
from instagramparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider)
    process.start()