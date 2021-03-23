# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.

# для определения уникальности используем url  вакансии
# 1) через insert_one
def add_vacancy(curvacancy, col):
    #col.replaceOne({'link': curvacancy['link']}, curvacancy, {'upsert': True})
    if not col.count_documents({'link': curvacancy['link']}):
        # таких вакансий нет- добавляем
        col.insert_one(curvacancy)

# 2) через replace_one
def add_vacancy1(curvacancy, col):
    try:
        col.replace_one({'link': curvacancy['link']}, curvacancy, upsert=True)
    except ValueError:
        print(ValueError)


# 3) добавление новых вакансии
for vacancy in data['hh']+data['superjob']:
    add_vacancy1(vacancy, vacancies)


print(vacancies.count())

