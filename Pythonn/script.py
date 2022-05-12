import requests
import json
import os
import sys
import datetime

url_users = 'https://json.medrating.org/users'  # указываем url api

url_todos = 'https://json.medrating.org/todos'

try:
    res_users = requests.get(url_users)  # Делаем запрос get по url api
except:
    print('Не удается подключиться к users API')
    sys.exit()

try:
    res_todos = requests.get(url_todos)
except:
    print('Не удается подключиться к todos API')
    sys.exit()

# Получаем text api и переводим его в list для работы
json_users = json.loads(res_users.text)
json_todos = json.loads(res_todos.text)

todo_number = 0  # Номер дела в цикле, отделяющим выполненные от невыполненных дел
users_todo = []  # Будущий cловарь с id пользователя, id его завершенных дел, id незавершенных дел и количеством дел всего

# Пробегаем по всем номерам элементов api users
for user_number in range(len(json_users)):
    completed_todo = []
    uncompleted_todo = []
    # При нахождении совпадений по ключу userId в todos и id в users
    while json_todos[todo_number].get('userId') == json_users[user_number].get('id'):
        # Если дело завершено, то добавляем его id в list completed_todo
        if json_todos[todo_number].get('completed'):
            completed_todo.append(json_todos[todo_number].get('id'))
        else:  # Иначе добавляем в list uncompleted_todo
            uncompleted_todo.append(json_todos[todo_number].get('id'))
        todo_number += 1  # Переходим к проверке следующего дела
    # Общее число дел пользователя
    count_todo = len(completed_todo) + len(uncompleted_todo)
    users_todo.append({'id': json_users[user_number].get(
        'id'), 'id_completed': completed_todo, 'id_uncompleted': uncompleted_todo, 'count_todo': count_todo})
    # В конце получаем словарь с id пользователя, id его завершенных дел, id незавершенных дел и количеством дел всего


def type_to_str(type):  # Функция преобразует тип в str. Необходимо для печати в файле
    type = "".join(map(str, type))
    return type


def cut_title(string):  # Функция обрезки строки до 48 символов
    if len(string) > 48:
        string = string[0:47] + '...'
    return string

# Функция подготовки к печати в файл названий дел пользователей


def titles_to_print(need, user_number):
    title_to_print = []
    # Пробегаем по всем делам пользователя
    for l in users_todo[user_number].get(need):
        # Добавляем в list название дела
        title_to_print.append(cut_title(json_todos[l - 1].get('title'))+'\n')
    # Преобразуем полученный list в строку для печати
    title_to_print = type_to_str(title_to_print)
    return title_to_print

# Функция подготавливает отчет для всех пользователей, у которых в API есть все необходимые для отчета данные


def print_report():
    if os.path.exists('tasks') == False:  # Проверка существования папки tasks
        os.mkdir('tasks')  # Создаем папку, если такой нет

    # Для каждого пользователя по его номеру подготавливаем list к печати в файл
    for user_number in range(len(json_users)):

        try:

            # Текущее время
            now = datetime.datetime.now()
            date_time_hour = now.strftime('%H')
            date_time_min = now.strftime('%M')
            date_year = now.strftime('%Y')
            date_month = now.strftime('%m')
            date_day = now.strftime('%d')
            date = type_to_str([date_day, '.', date_month, '.',
                               date_year, ' ', date_time_hour, ':', date_time_min])

            username = json_users[user_number].get('username')
            name_of_user = json_users[user_number].get('name')
            users_company_name = json_users[user_number].get(
                'company').get('name')
            users_email = json_users[user_number].get('email')
            completed_todo = users_todo[user_number].get('id_completed')
            uncompleted_todo = users_todo[user_number].get('id_uncompleted')
            users_number_todo = users_todo[user_number].get('count_todo')
            titles_completed = titles_to_print(
                'id_completed', user_number)
            titles_completed = titles_to_print(
                'id_uncompleted', user_number)

            # Проверка на существование отчета пользователя
            if os.path.exists('tasks/'+username+'.txt'):
                os.rename("tasks/"+username+".txt", "tasks/old_"+username+"_"+date_year +  # Если нашелся, то переименовываем
                          "-"+date_month+"-"+date_day+"T"+date_time_hour+"."+date_time_min+".txt")
            # Готовим list с данными для печати
            text_to_print = ['Отчет для ', users_company_name, '.\n',
                             name_of_user, ' <', users_email, '> ', date, '\n',
                             'Всего задач: ', users_number_todo, '\n\n',
                             'Завершенные задачи (', len(
                                 completed_todo), '): \n',
                             titles_completed, '\n\n',
                             'Оставшиеся задачи (', len(
                                 uncompleted_todo), '): \n',
                             titles_completed]
            text_to_print = type_to_str(text_to_print)  # Переводим list в str
            # Создаем файл с отчетом пользователя
            new_file = open("tasks/"+username+".txt", "w+")
            # Печатаем подготовленный скриптом отчет
            new_file.write(text_to_print)
            new_file.close()
        except:
            print('Api для пользователя номер ',
                  user_number, ' составлен неверно')


print_report()
