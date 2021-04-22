import db
import configparser
import schedule
import time
from threading import *
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

config = configparser.ConfigParser()
config.read("settings.ini", encoding="utf-8")

vk_session = vk_api.VkApi(token=config['settings']['token'])

lp = VkLongPoll(vk_session)
vk = vk_session.get_api()


# Отправить сообщение
def send_message(account_id, message, keyboard=None, attachment=None, forward_messages=None):
    vk.messages.send(user_id=account_id, message=message, keyboard=keyboard, random_id=get_random_id(),
                     attachment=attachment, forward_messages=forward_messages)


# Имя_Фамилия пользователя
def give_name(account_id):
    account = vk.users.get(user_ids=account_id)
    name = "[id{}|{} {}]".format(account_id, account[0]['first_name'], account[0]['last_name'])
    return name


# Имя_Фамилия пользователя
def give_start(account_id):
    account = vk.users.get(user_ids=account_id)
    name = "[id{}|{}]".format(account_id, account[0]['first_name'])
    return name


# Настройки
IMG_REG = config['texts']['img_reg']
IMG_SUC = config['texts']['img_suc']
IMG_FAIL = config['texts']['img_fail']
IMG_RATING = config['texts']['img_rating']
CODE = config['settings']['code']
DATE = config['settings']['date']
TOP_COUNT = int(config['settings']['top_count'])


# Настройки текстов
texts = {
    'suc_reg': config['texts']['suc_reg'].replace('\\n', '\n'),
    'fail_menu': config['texts']['fail_menu'].replace('\\n', '\n'),
    'error': config['texts']['error'].replace('\\n', '\n'),

    'score': config['texts']['score'].replace('\\n', '\n'),
    'suc_rating': config['texts']['suc_rating'].replace('\\n', '\n').format(TOP_COUNT),
    'fail_rating': config['texts']['fail_rating'].replace('\\n', '\n'),

    'new_video': config['texts']['new_video'].replace('\\n', '\n'),
    'suc_new_video': config['texts']['suc_new_video'].replace('\\n', '\n'),
    'exit': config['texts']['exit'].replace('\\n', '\n'),

    'suc_video': config['texts']['suc_video'].replace('\\n', '\n'),
    'fail_video': config['texts']['fail_video'].replace('\\n', '\n'),

    'suc_reg_adm': config['texts']['suc_reg_adm'].replace('\\n', '\n'),
    'suc_adm': config['texts']['suc_adm'].replace('\\n', '\n'),
    'fail_adm': config['texts']['fail_adm'].replace('\\n', '\n'),

    'suc_first_video': config['texts']['suc_first_video'].replace('\\n', '\n'),
    'fail_first_video': config['texts']['fail_first_video'].replace('\\n', '\n'),
    'adm_score': config['texts']['adm_score'].replace('\\n', '\n'),

    'coupon_1': config['texts']['coupon_1'].replace('\\n', '\n'),
    'coupon': config['texts']['coupon'].replace('\\n', '\n'),
    'suc_coupon': config['texts']['suc_coupon'].replace('\\n', '\n')
}


# Списки
new_video = []
adm = []
adm_video = []


# Переменные
rating = ''


# Клавиатуры
keyboard_main = VkKeyboard(one_time=False)
keyboard_main.add_button('Загрузить видео', color=VkKeyboardColor.POSITIVE)
keyboard_main.add_line()
keyboard_main.add_button('Рейтинг', color=VkKeyboardColor.SECONDARY)
keyboard_main.add_button('Мои баллы', color=VkKeyboardColor.PRIMARY)

keyboard_video_exit = VkKeyboard(one_time=False)
keyboard_video_exit.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

keyboard_adm = VkKeyboard(one_time=False)
keyboard_adm.add_button('Модерация видео', color=VkKeyboardColor.POSITIVE)
keyboard_adm.add_line()
keyboard_adm.add_button('Назад', color=VkKeyboardColor.NEGATIVE)

keyboard_adm_video = VkKeyboard(one_time=False)
keyboard_adm_video.add_button('Принять', color=VkKeyboardColor.POSITIVE)
keyboard_adm_video.add_button('Отказать', color=VkKeyboardColor.NEGATIVE)
keyboard_adm_video.add_line()
keyboard_adm_video.add_button('Назад', color=VkKeyboardColor.SECONDARY)


def sh_rating():
    try:
        global rating
        db_rating = db.account_select_rating()
        rating = texts['suc_rating']
        num = 1
        for account in db_rating:
            if num <= int(TOP_COUNT):
                rating += '{}: {} баллов\n'.format(give_name(account[1]), account[0])
                num += 1
    except:
        rating = texts['fail_rating']


schedule.every().minute.at(":00").do(sh_rating)


def while_sh(arg):
    while True:
        schedule.run_pending()
        time.sleep(1)


sh_rating()


sh_rating = Thread(target=while_sh, args=(1, ), daemon=True)
sh_rating.start()


for event in lp.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.from_user:
        account_id = event.user_id
        message = event.text
        try:
            if db.account_exits(account_id):
                if account_id in new_video:
                    if message == 'Назад':
                        new_video.remove(account_id)
                        send_message(account_id, texts['exit'], keyboard_main.get_keyboard())
                    else:
                        message_id = event.message_id
                        db.video_insert(account_id, event.message_id)
                        send_message(account_id, texts['suc_new_video'], keyboard_video_exit.get_keyboard())

                elif account_id in adm:

                    # Оценка видео
                    if account_id in adm_video:
                        v = db.video_select_adm(account_id)
                        if message == 'Назад':
                            db.video_update_adm_id(v['video_id'], None)
                            adm_video.remove(account_id)
                            send_message(account_id, texts['exit'], keyboard_adm.get_keyboard())
                        elif message.isdigit() or message == 'Принять' or message == 'Отказать':
                            if message.isdigit():
                                score = int(message)
                            elif message == 'Принять':
                                score = 1
                            elif message == 'Отказать':
                                score = 0
                            db.video_update_score(v['video_id'], score)
                            send_message(account_id, texts['adm_score'], keyboard_adm.get_keyboard())
                            adm_video.remove(account_id)
                            if score > 0:
                                send_message(account_id=v['account_id'],
                                             message=texts['suc_video'].format(score, give_name(v['account_id']), score, DATE),
                                             attachment=IMG_SUC,
                                             forward_messages=v['message_id'])
                            else:
                                send_message(account_id=v['account_id'],
                                             message=texts['fail_video'],
                                             attachment=IMG_FAIL,
                                             forward_messages=v['message_id'])
                        else:
                            send_message(account_id, texts['fail_menu'], keyboard_adm_video.get_keyboard())

                    # Модерация
                    elif message == 'Модерация видео':
                        v_f = db.video_select_first()
                        # Вывод информации о видео
                        if v_f:
                            adm_video.append(account_id)
                            db.video_update_adm_id(v_f['video_id'], account_id)
                            send_message(account_id=account_id,
                                         message=texts['suc_first_video'].format(v_f['video_id'], v_f['account_id']),
                                         forward_messages=v_f['message_id'],
                                         keyboard=keyboard_adm_video.get_keyboard())

                        # Вывод информации об отсутствии видео
                        else:
                            send_message(account_id, texts['fail_first_video'], keyboard_adm.get_keyboard())


                    # Выдача сетификатов
                    elif message == '/sertif':

                        r = db.account_select_rating()
                        count = 1
                        for i in r:
                            if TOP_COUNT >= count:
                                if count == 1:
                                    send_message(i[1], texts['coupon_1'])
                                else:
                                    send_message(i[1], texts['coupon'].format(count))
                                count += 1

                        send_message(account_id, texts['suc_coupon'], keyboard_adm.get_keyboard())

                    # Вернуться назад
                    elif message == 'Назад':
                        adm.remove(account_id)
                        send_message(account_id, texts['exit'], keyboard_main.get_keyboard())

                    # Команды не существует
                    else:
                        # Команды нету
                        send_message(account_id, texts['fail_menu'], keyboard_adm.get_keyboard())

                elif message == 'Загрузить видео':
                    new_video.append(account_id)
                    send_message(account_id, texts['new_video'], keyboard_video_exit.get_keyboard())

                elif message == 'Мои баллы':
                    score = db.video_select_sum(account_id)
                    send_message(account_id, texts['score'].format(score), keyboard_main.get_keyboard())

                elif message == 'Рейтинг':
                    send_message(account_id, rating, keyboard_main.get_keyboard(), attachment=IMG_RATING)

                elif message == '/adm':
                    if db.admin_exits(account_id):
                        adm.append(account_id)
                        send_message(account_id, texts['suc_adm'], keyboard_adm.get_keyboard())
                    else:
                        send_message(account_id, texts['fail_adm'], keyboard_main.get_keyboard())

                elif message == CODE:
                    db.admin_insert(account_id)
                    send_message(account_id, texts['suc_reg_adm'], keyboard_main.get_keyboard())

                #else:
                    ## Информация об отсутсвии команды
                    #send_message(account_id, texts['fail_menu'], keyboard_main.get_keyboard())
            elif message.lower() == 'start':
                if db.account_insert(account_id):
                    send_message(account_id, texts['suc_reg'].format(give_start(account_id)), keyboard_main.get_keyboard(), attachment=IMG_REG)
        except:
            send_message(account_id, texts['error'], keyboard_main.get_keyboard())
