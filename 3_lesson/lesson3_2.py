# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.

def print_vacancy(vacancies):
    mysalary = input('Укажите минимальную зарплату : ')
    try:
        mysalary = float(mysalary)
    except:
        mysalary = 0
    for vacancy in vacancies.find({'$or':[{'salary_min':{'$gt':mysalary}}, {'salary_max':{'$gt':mysalary}}]}):
         pprint(vacancy)

print_vacancy(vacancies)
