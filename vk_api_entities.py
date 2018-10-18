import requests
import time


class EntityVK:
    """ Прототип экземпляров описывающих объекты VK
        Абстрактный родительский класс"""
    _token = 'ed1271af9e8883f7a7c2cefbfddfcbc61563029666c487b2f71a5227cce0d1b533c4af4c5b888633c06ae'

    def __init__(self, id):
        self._id = id

    def __str__(self):
        return 'Имя объекта API VK: https://vk.com/'

    def set_token(self, token):
        self._token = token

    @property
    def _params(self):
        return {
            'access_token': self._token,
            'v': '5.85',
        }

    @property
    def info(self):
        return 'Объект API VK'

    @staticmethod
    def _info_request(method, params):
        while True:
            response = requests.get(f'https://api.vk.com/method/{method}', params).json()
            if 'error' in response and response['error']['error_code'] == 6:
                print(response['error']['error_msg'], '- ожидаем 1 сек.')
                time.sleep(1)
            else:
                time.sleep(0.34)
                break
        return response


class GroupVK(EntityVK):
    """ Прототип экземпляров описывающих группы VK
        Экземпляр группы создается на основе идентификатора группы VK"""

    def __str__(self):
        name = self.info[0]['name']
        screen_name = self.info[0]['screen_name']
        return f'{name}: https://vk.com/{screen_name}'

    @property
    def info(self):
        params = self._params
        params['group_id'] = self._id
        params['extended'] = 1
        params['fields'] = ['members_count']
        method = 'groups.getById'
        response = super()._info_request(method, params)
        if 'error' in response:
            return response['error']
        return response['response']

    @property
    def members(self):
        EXECUTE_STEP = 25000
        members_count = self.info[0]['members_count']
        progress_counter = int(members_count / EXECUTE_STEP)
        params = self._params
        method = 'execute'
        members = []

        print('■' * progress_counter, end='', flush=True)

        for i in range(0, members_count, EXECUTE_STEP):
            code = f"""
                        var step=1000, R, offset = {i}, loop=0,
                        out = {{ oid: {self._id}, ids:[], mass: {members_count}, offset: 0, next: 0 }};

                        while( offset <= out.mass  &&  loop < {EXECUTE_STEP / 1000}) {{
                            R = API.groups.getMembers({{ "group_id": out.oid, "sort": "id_asc", "offset": offset, "count": step}});
                            if( !!R.items  &&  R.items.length > 0) {{
                                out.ids.push( R.items);
                                out.mass = R.count;

                                out.loop = loop;

                                out.offset = offset;
                                offset = offset + step;
                                out.next = offset;

                                loop = loop + 1;
                            }} else {{
                                out.error = "Empty items";
                                out.r = R;
                                return out;
                            }}
                        }}

                        return out;
                    """
            params['code'] = code
            response = super()._info_request(method, params)

            if 'error' in response:
                return response['error']

            for lst in response['response']['ids']:
                members.extend(lst)

            progress_counter = progress_counter - 1
            print('', end='\r', flush=True)
            print('\u25A0' * progress_counter, end='', flush=True)

        return members


class UserVK(EntityVK):
    """ Прототип экземпляров описывающих пользователей VK
    Экземпляр класса создается на основе идентификатора пользователя VK"""

    def __init__(self, id):
        super().__init__(id)
        self._user_id = self.info[0]['id']

    def __str__(self):
        first_name = self.info[0]['first_name']
        last_name = self.info[0]['last_name']
        return f'{first_name} {last_name}: https://vk.com/id{self._id}'

    @property
    def info(self):
        params = self._params
        params['user_ids'] = self._id
        method = 'users.get'
        response = super()._info_request(method, params)
        if 'error' in response:
            return response['error']
        return response['response']

    @property
    def friends(self):
        params = self._params
        params['user_id'] = self._user_id
        method = 'friends.get'
        response = super()._info_request(method, params)
        if 'error' in response:
            return response['error']
        return response['response']['items']

    @property
    def groups(self):
        params = self._params
        params['user_id'] = self._user_id
        method = 'groups.get'
        response = super()._info_request(method, params)
        if 'error' in response:
            return response['error']
        return response['response']['items']
