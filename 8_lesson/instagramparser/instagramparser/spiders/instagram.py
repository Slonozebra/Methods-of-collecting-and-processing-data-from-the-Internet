import scrapy
from scrapy.http import HtmlResponse
from instagramparser.items import InstagramparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    insta_login = 'student_gb_parsing'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:9:1617360256:AVdQAKxnMwrgGE92JU9CX0Nn1IbSJTD0o0zCCSY0Ct9l8hQBv/W0NWlswQyEXJ8edMvGRIglgcVsAm8mhoFxKlxQnEDmcnvjFwdXuuTSPyY6iX+txuGrAc7B2NM+DrE7E4yNr5JOU1QxVsnc'
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_users = ['paris_photographer_vadim', '384studio']

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    posts_hash = 'eddbde960fed6bde675388aac39a3657'
    followers_hash = 'c76146de99bb02f6415203be841dd25a'
    following_hash = 'd04b0a864b4b54837c0d870b0e77e076'

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token})


    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for parse_user in self.parse_users:
                yield response.follow(
                    f'/{parse_user}',
                    callback=self.user_data_parse,  # след. шаг
                    cb_kwargs={'username': parse_user}
                )


    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id,
                     'first': 10}


        url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
        url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
        yield response.follow(
            url_followers,
            callback=self.followers_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)})

        yield response.follow(
            url_following,
            callback=self.following_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)})

 # собираем посты
    def user_posts_parse(self, response: HtmlResponse, username, user_id,
                          variables):
         j_data = json.loads(response.text)
         page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
         if page_info.get('has_next_page'):  # Если есть следующая страница
             variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
             url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
             yield response.follow(
                 url_posts,
                 callback=self.user_posts_parse,
                 cb_kwargs={'username': username,
                            'user_id': user_id,
                            'variables': deepcopy(variables)}
             )
         posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')
         for post in posts:
             item = InstaparserItem(
                 user_id=user_id,
                 photo=post['node']['display_url'],
                 likes=post['node']['edge_media_preview_like']['count'],
                 post=post['node']
             )
         yield item

    # собираем подписчиков
    def followers_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        followers_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        print("followers_info =", followers_info)
        if followers_info.get('has_next_page'):
            variables['after'] = followers_info['end_cursor']
            print("variables['after'] =", variables['after'])
            url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
            print("url_followers =", url_followers)
            yield response.follow(
                url_followers,
                callback=self.followers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)
                           }
            )
        followers = j_data.get('data').get('user').get('edge_followed_by').get('edges')  # Сами подписчики
        for follower in followers:
            item = InstagramparserItem(
                username=username,
                follower_id=follower['node']['id'],
                username_follower=follower['node']['username'],
                full_name=follower['node']['full_name'],
                photo=follower['node']['profile_pic_url'],
                user_attribute='follower',
                full_info=follower['node'])
        yield item

    # собираем тех, на кого подписан пользователь
    def following_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        following_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        print("following_info =", following_info)
        if following_info.get('has_next_page'):
            variables['after'] = following_info['end_cursor']
            print("variables['after'] =", variables['after'])
            url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
            print("url_following =", url_following)
            yield response.follow(
                url_following,
                callback=self.following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)})
        followings = j_data.get('data').get('user').get('edge_follow').get('edges')
        for following in followings:
            item = InstagramparserItem(
                username=username,
                following_id=following['node']['id'],
                username_following=following['node']['username'],
                full_name=following['node']['full_name'],
                photo=following['node']['profile_pic_url'],
                user_attribute='following',
                full_info=following['node'])
        yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя. 
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
