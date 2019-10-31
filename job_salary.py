import os
import requests
from dotenv import load_dotenv
import statistics
import terminaltables


def get_predict_salary(salary_from, salary_to):
    if salary_from in (None, 0) and salary_to in (None, 0):
        return None

    if salary_from in (None, 0):
        return salary_to * 0.8

    if salary_to in (None, 0):
        return salary_from * 1.2

    return (salary_to - salary_from) / 2


def predict_rub_salary_headhunter(vacancy):
    if vacancy['salary'] is None or vacancy['salary']['currency'] != 'RUR':
        return None

    return get_predict_salary(vacancy['salary']['from'],
                              vacancy['salary']['to'])


class NoSuchTown(Exception):
    pass


def find_headhunter_area_recursive(areas, text):
    for area in areas:
        if area['name'] == text:
            return area['id']
        if area['areas']:
            area_id = find_headhunter_area_recursive(area['areas'], text)
            if area_id is not None:
                return area_id


def get_headhunter_area_id(area):
    ares_url = 'https://api.hh.ru/areas'

    response = requests.get(url=ares_url)
    response.raise_for_status()
    area_id = find_headhunter_area_recursive(areas=response.json(), text=area)
    if not area_id:
        raise NoSuchTown('Город HeadHunter не найден')
    return area_id


def get_headhunter_vacancies(text, area_id, period):
    vacancies = []
    url = 'https://api.hh.ru/vacancies'
    params = {
        'page': 0,
        'per_page': 40,
        'text': text,
        'area': area_id,
        'period': period,
        'vacancy_search_fields': 'name'
    }

    while True:
        response = requests.get(url, params=params)
        response.raise_for_status()
        pages = response.json()['pages']
        vacancies += response.json()['items']
        params['page'] += 1
        if params['page'] >= pages:
            break

    return vacancies


def predict_headhunter_vacancies(languages, area=None, period=None):
    vacancies = {}
    area_id = get_headhunter_area_id(area) if area is not None else None

    for language in languages:
        vacancies_found = get_headhunter_vacancies(
            text=f'Программист {language}',
            area_id=area_id, period=30)
        salaries = list(filter(lambda x: x is not None,
                               (predict_rub_salary_headhunter(vacancy) for
                                vacancy in
                                vacancies_found)))
        vacancies[language] = {
            "vacancies_found": len(vacancies_found),
            "vacancies_processed": len(salaries),
            "average_salary": int(statistics.mean(salaries))
        }
    return vacancies


def get_superjob_area_id(keyword):
    url = "https://api.superjob.ru/2.0/towns/"
    params = {'keyword': keyword, 'all': True}
    response = requests.get(url, params=params)
    response.raise_for_status()
    if len(response.json()['objects']) < 1:
        raise NoSuchTown('Город SuperJob не найден')
    return response.json()['objects'][0]['id']


def get_superjob_vacancies(api_key, keyword, area_id, catalogues=None):
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {'X-Api-App-Id': api_key}
    params = {
        'keyword': keyword,
        'catalogues': catalogues,
        'page': 0,
        'count': 100
    }
    if area_id is not None:
        params['town'] = area_id

    vacancies = []
    while True:
        response = requests.get(url=url, params=params, headers=headers)
        response.raise_for_status()
        pages = response.json()['total']
        vacancies += response.json()['objects']
        params['page'] += 1
        if params['page'] >= pages:
            break

    return vacancies


def predict_rub_salary_superjob(vacancy):
    if vacancy['currency'] != 'rub':
        return None

    return get_predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def predict_superjob_vacancies(api_key, languages,
                               area=None, catalogues=None):
    vacancies = {}
    area_id = get_superjob_area_id(area) if area is not None else None

    for language in languages:
        vacancies_found = get_superjob_vacancies(api_key,
                f'Программист {language}', area_id, catalogues)
        salaries = list(filter(lambda x: x is not None,
                               (predict_rub_salary_superjob(vacancy)
                                for vacancy in vacancies_found)))
        vacancies[language] = {
            "vacancies_found": len(vacancies_found),
            "vacancies_processed": len(salaries),
            "average_salary": int(statistics.mean(salaries))
        }
    return vacancies


def print_vacancies_table(vacancies, title):
    table_header = [
        ('Язык программирования', 'Найдено вакансий', 'Обработано вакансий',
        'Средняя зарплата, руб.')
    ]
    for language, stat in vacancies.items():
        table_header.append([language,
                               stat['vacancies_found'],
                               stat['vacancies_processed'],
                               stat['average_salary']])
    table = terminaltables.AsciiTable(table_header, title)
    print(table.table)


def main():
    load_dotenv()
    languages = [
        'Java',
        'Python',
        'PHP',
        'C',
        'C++',
        'C#',
        'Go',
        'JavaScript'
    ]

    try:
        headhunter_vacancies = predict_headhunter_vacancies(languages=languages,
                                                            area='Москва',
                                                            period=30)
        print_vacancies_table(headhunter_vacancies, 'HeadHunter Moscow')

        superjob_api_key = os.getenv('SUPERJOB_API_KEY')
        if superjob_api_key:
            superjob_vacancies = predict_superjob_vacancies(
                superjob_api_key, languages, 'Москва')
            print_vacancies_table(superjob_vacancies, 'SuperJob Moscow')

    except NoSuchTown as error:
        print(f'Error: {error}')


if __name__ == '__main__':
    main()
