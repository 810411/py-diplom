import json
import os
import sys
from vk_api_entities import GroupVK, UserVK

current_dir = os.path.dirname(os.path.abspath(__file__))


def print_help():
    print('Шпионские игры')
    print('Выводит список групп в ВК в которых состоит пользователь, но не состоит никто из его друзей')
    print('Результат сохраняет в виде фала JSON в текущую папку')
    print('<id> - параметр коммандной строки, где id имя пользователя или его id в ВК')
    print('Если <id> пропущен, скрипт запросит ввод id через консоль\n')


def do_crossing(user_):
    user_friends = user_.friends
    user_croups = user_.groups
    counter = len(user_croups)
    result_ = [[], []]

    for group_id in user_croups:
        print('Осталось обработать записей:', counter)
        counter -= 1
        group = GroupVK(group_id)
        is_friends_not_in_group = set(group.members).isdisjoint(set(user_friends))
        if is_friends_not_in_group:
            result_[0].append(f'{group}')
            result_[1].append(group.info)
    return result_


def spying_on_user(user_id):
    user = UserVK(user_id)
    path_to_save = os.path.join(current_dir, f'{user_id}-groups.json')
    result = do_crossing(user)

    print('Пользователь', user)
    print('Список групп в ВК в которых состоит пользователь, но не состоит никто из его друзей:')
    for item in result[0]:
        print(item)

    with open(path_to_save, "w", encoding="utf-8") as file:
        json.dump(result[1], file, indent=2, separators=(',', ': '), ensure_ascii=False)
        print(f'Данные сохранены в {path_to_save}')


if __name__ == "__main__":
    print_help()

    try:
        id_ = sys.argv[1]
    except IndexError:
        while True:
            id_ = input('Введите имя пользователя или его id в ВК: ')
            if id_:
                break

    spying_on_user(id_)
