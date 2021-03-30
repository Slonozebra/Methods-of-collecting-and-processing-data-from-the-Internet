# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
# записывающую собранные вакансии в созданную БД.

from pymongo import MongoClient
import json
from pprint import pprint


data = json.load(open("vacancies.json"))
for vac in (data['hh'] +  data['superjob']):
    try:
        vac['salary_min']=float(vac['salary_min'])
    except:
        vac['salary_min']=None
    try:
        vac['salary_max']=float(vac['salary_max'])
    except:
        vac['salary_max']=None

client = MongoClient( 'localhost' , 27017 )
db = client[ 'vacancies_db' ]
vacancies = db.vacancies
vacancies.drop()
vacancies.insert_many(data['hh'])
vacancies.insert_many(data['superjob'])