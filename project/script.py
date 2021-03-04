import json
import os
import vk_api
from vk_api import VkApi
from time import sleep as wait

# TODO: make the get_wall function output easy to understand, edit the target_id receiver,
#  complete repeater function, create dictionary with commands instead if using if else statements

people = {
    'Ilya': 366432824,
    'me': 519266666,
    'barsa': 462044945,
}


class Oleg(object):

    def __init__(self, vk):
        self.__vk = vk
        self.__target_id = ''

    @property
    def id(self):
        return self.__target_id

    @id.setter
    def id(self, val):
        self.__target_id = val

    def post_wall(self, msg: str):
        self.__vk.method('wall.post', {
            'owner_id': self.__target_id,
            'message': msg
        })

    def get_wall(self):
        val = self.__vk.method('wall.get', {
            'owner_id': self.__target_id
        })
        return val

    def comment(self, post_id: int, msg: str):
        self.__vk.method('wall.createComment', {
            'owner_id': self.__target_id,
            'post_id': post_id,
            'message': msg
        })

    def offline_mode(self):
        self.__vk.method('account.setOffline')


class FileManager(object):
    def __init__(self):
        self.__basedir = os.path.dirname(os.path.abspath(__file__))
        self.__conf = None

    def config_file_location(self):
        for file in os.listdir(self.__basedir):
            if file.startswith('vk_config') and file.endswith('.json'):
                return self.__basedir + file
        return None

    @property
    def conf(self):
        return self.__conf

    @conf.setter
    def conf(self, val):
        self.__conf = val

    @staticmethod
    def recv_data():
        data = json.load(open('vk_config.v2.json', 'r'))
        return data

    def config_file_del(self, save=True):
        if not save:
            print('WARNING!\nYou are deleting your config file, do you wish to continue?')
            if not y_n():
                return 'aborted'
            for file in os.listdir(self.__basedir):
                if file.startswith('vk_config') and file.endswith('.json') and not save:
                    os.remove('vk_config.v2.json')
                    return 'config file deleted'
            return 'no config file found'
        return 'config file saved'

    @property
    def d(self):
        return self.__basedir

    @d.setter
    def d(self, val):
        self.__basedir = val


def y_n():

    while True:

        try:
            answer = input('[Y] [N]\n>>').lower()
            if answer not in ['y', 'n']:
                raise ValueError
            return answer == 'y'

        except ValueError:
            print('Please try again')


def set_limit(s):

    while True:

        try:
            limit = int(input(f'{s}: '))
            if limit == -1:
                return None
            if limit < 1:
                raise ValueError
            return limit

        except ValueError:
            print('Please try again')


def interactive_vk_login():
    login = input('login\n>> ')
    password = input('password\n>> ')
    vk = VkApi(login, password)
    limit = set_limit('Set limit of tries')
    tries = 0
    while True:
        try:
            vk.auth()
            print('success')
            return vk
        except vk_api.VkApiError:
            if limit:
                if tries == limit:
                    print('Change password? ([Y], [N])')
                    change = y_n()
                    if change:
                        password = input('password\n>> ')
                        vk = VkApi(login, password)
                    print('Change limit? ([Y], [N])')
                    change = y_n()
                    if change:
                        limit = set_limit('Set limit of tries')
                        tries = 0
                tries += 1
            print('login failed, starting a new attempt in 5 sec')
            wait(5)


def vk_login(login: str) -> object:
    vk = VkApi(login, '')
    try:
        vk.auth()
        return vk
    except vk_api.VkApiError:
        print('login failed')


def use_token(data):
    print('You have already logged in earlier, use previous token and login?')
    answer = y_n()
    if answer:
        login = list(data.keys())[0]
        logged_in = vk_login(login)
        if logged_in:
            return logged_in
        else:
            print('Config file access token timed out')


def main():

    commands = {
        'target id': 'Sets target ID',
        'edit': 'Login into a different account for the SB',
        'post wall': 'Posts input message on targets wall',
        'delete config file': '',
        'get wall': 'Return ID and contents of targets wall posts',
        'comment': 'Comments on the given post',
        'exit': 'exits the program',
        'print target id': '',
        'repeater': 'repeats given function',
        'repeater list': 'lists all functions that can be repeated'
    }

    repeat_l = ['post wall', 'comment wall']

    self_bot = ''

    file_manager = FileManager()
    config_file = file_manager.config_file_location()

    # Checks if the config file exists and extracts the login from the json config file

    if config_file:

        data = file_manager.recv_data()

        logged_in = use_token(data)

        if logged_in:
            self_bot = Oleg(logged_in)

    if not self_bot:

        self_bot = Oleg(interactive_vk_login())

    print('Do you wish to save config file?')
    print(file_manager.config_file_del(y_n()))

    # the main loop
    while True:

        self_bot.offline_mode()

        cmd = input('>>').lower()

        if cmd == 'edit':
            # resets the SB object with an interactive login
            self_bot = Oleg(interactive_vk_login())

        elif cmd == 'target id':
            # this is done poorly, will be edited later
            while True:
                try:
                    target = input('Enter target name or id >>')
                    self_bot.id = (int(target) if target.isdigit() else people[target])
                    break
                except KeyError:
                    print('bad input')

        # All functions for posting only support messages for now, attachments will come soon
        elif cmd == 'post wall':
            msg = input('Type your message:\n')
            self_bot.post_wall(msg)

        elif cmd == 'delete config file':
            file_manager.config_file_del(False)

        # Gets the ID and contents of every post on the targets wall.
        elif cmd == 'get wall':
            print(self_bot.get_wall())

        elif cmd == 'comment':
            post_id = int(input('Enter post id:\n'))
            msg = input('Enter message:\n')
            self_bot.comment(post_id, msg)

        elif cmd == 'print target id':
            print(self_bot.id or 'No target set')

        elif cmd == 'exit':
            return

        elif cmd == 'help':
            for command in commands:
                print(f"{command} - {commands[command] or 'explains itself'}")

        elif cmd == 'repeater':
            while True:
                cmd = input('> ')
                if cmd in repeat_l:
                    while True:

                        count = 0
                        f = None
                        post_id = None
                        limit = set_limit('Set limit of requests')
                        gap = set_limit('Set gap between requests')
                        msg = input('Enter your message: ')
                        if cmd == 'post wall':
                            f = self_bot.post_wall

                        elif cmd == 'comment wall':
                            post_id = int(input('Enter post id: '))
                            f = self_bot.comment

                        while count < limit:

                            if post_id:
                                f(post_id, msg)

                            else:
                                f(msg)

                            count += 1
                            wait(gap)

                        break

                elif cmd == 'exit':
                    break

                else:
                    print('unknown command')

        elif cmd == 'repeater list':
            print('\n'.join(repeat_l))

        else:
            print('unknown command')


if __name__ == '__main__':
    main()
