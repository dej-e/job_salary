# Сравниваем вакансии программистов

Скрипт считает статистику по вакансиям и заработной плате от сервисов [HeadHunter](https://hh.ru) и [SuperJob](https://superjob.ru) для г.Москва.


### Как установить

Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

Для работы скрипта с сервисом SuperJob
 необходимо зарегистрироваться на этом сервисе и получить Secret key.

После клонирования проекта создайте в корень файл .env с таким содержимым:
```
SUPERJOB_KEY=_ваш secret key от SuperJob_
```
### Для получения Secret key  от SuperJob:
* Перейдите по ссылке [https://api.superjob.ru/register](https://api.superjob.ru/register)
* Следуйте инструкции для регистрации приложения и получения кода
* Скопируйте Secret key в файл .env как указано выше 

### Пример запуска

```python job_salary.py```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).