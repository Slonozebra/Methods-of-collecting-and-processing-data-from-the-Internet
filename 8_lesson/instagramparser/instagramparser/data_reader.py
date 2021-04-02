#4) Написать функцию, которая будет делать запрос к базе, который вернет список подписчиков только указанного пользователя
#5) Написать функцию, которая будет делать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь
from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['instagram']

follows = db.follows

print('Followers:')
for follow in follows.find({'username': 'paris_photographer_vadim', 'user_attribute': 'follower'}, {'username_follower': 1}):
    pprint(follow)
print('Followings:')
for follow in follows.find({'username': '384studio', 'user_attribute': 'following'}, {'username_following':1}):
    pprint(follow)