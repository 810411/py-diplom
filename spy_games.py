import json
import os
import sys
import time
from multiprocessing import Process
from vk_api_entities import GroupVK, UserVK

current_dir = os.path.dirname(os.path.abspath(__file__))


def print_help():
    return """
            Шпионские игры
    Выводит список групп в ВК в которых состоит пользователь, но не состоит никто из его друзей
    Результат сохраняет в виде фала JSON в текущую папку
    <id> - параметр коммандной строки, где id имя пользователя или его id в ВК
    Если <id> пропущен, скрипт запросит ввод id через консоль
    """


def do_crossing(user_friends_, user_croups_):
    result_ = [[], []]

    for group_id in user_croups_:
        group = GroupVK(group_id)
        is_friends_not_in_group = set(group.members).isdisjoint(set(user_friends_))

        if is_friends_not_in_group:
            result_[0].append(f'{group}')
            result_[1].append(group.info)
    return result_


def set_timer(user_croups_):
    execute_step = 25000
    counter = 0

    for group_id in user_croups_:
        group = GroupVK(group_id)
        counter += group.info[0]['members_count']
    return counter / execute_step


def reduce_timer(user_croups_):
    msecs = int(set_timer(user_croups_))
    step = 1

    for i in range(0, msecs + 1, step):
        timer = time.strftime('%H:%M:%S', time.gmtime(msecs))
        print('', end='\r', flush=True)
        print(f'Осталось: {timer}', end='', flush=True)
        time.sleep(step)
        msecs -= step


if __name__ == "__main__":
    print(print_help())

    try:
        id_ = sys.argv[1]
    except IndexError:
        while True:
            id_ = input('Введите имя пользователя или его id в ВК: ')
            if id_:
                break

    print('Подождите! Обрабатываются запросы к API')

    user = UserVK(id_)
    user_croups = user.groups

    proc = Process(target=reduce_timer, args=(user_croups,))
    proc.start()

    user_friends = user.friends
    result = do_crossing(user_friends, user_croups)

    proc.join()

    print('\nПользователь', user)
    print('Список групп в ВК в которых состоит пользователь, но не состоит никто из его друзей:')
    for item in result[0]:
        print(item)

    path_to_save = os.path.join(current_dir, f'{id_}-groups.json')
    with open(path_to_save, "w", encoding="utf-8") as file:
        json.dump(result[1], file, indent=2, separators=(',', ': '), ensure_ascii=False)
        print(f'Данные сохранены в {path_to_save}')
