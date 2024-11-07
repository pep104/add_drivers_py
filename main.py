from datetime import datetime
import json
import uuid
import requests
import telebot
from keys import token, url_get_work_rules, park_id, X_API_Key, X_Client_id, url_post_walking, url_post_auto, \
    url_post_create_car, url
from telebot import types

bot = telebot.TeleBot(token)
driver = {
    'driver_id': ''
}
data_post_auto = {
    "account": {
        "balance_limit": "5",
        "block_orders_on_balance_below_limit": True,
        "work_rule_id": ""
    },
    "order_provider": {
        "partner": True,
        "platform": False
    },
    "person": {
        "contact_info": {
            "phone": ""
        },
        "driver_license": {
            "country": "",
            "expiry_date": "",
            "issue_date": "",
            "number": ""
        },
        "driver_license_experience": {
            "total_since_date": ""
        },
        "full_name": {
            "first_name": "",
            "last_name": "",
            "middle_name": ""
        }
    },
    "profile": {
        "hire_date": f"{datetime.now().year}-{datetime.now().month}-{datetime.now().day}"
    }
}

data_post_walking = {
    "birth_date": "",
    "full_name": {
        "first_name": "",
        "last_name": "",
        "middle_name": ""
    },
    "phone": "",
    "work_rule_id": ""
}

data_post_create_car = {
    "cargo": {
        "cargo_hold_dimensions": {
            "height": 0,
            "length": 0,
            "width": 0
        }
    },
    "child_safety": {
        "booster_count": 0
    },
    "park_profile": {
        "callsign": "",
        "leasing_conditions": {
            "company": "leasing company",
            "interest_rate": "0",
            "monthly_payment": 0,
            "start_date": "2022-01-01",
            "term": 0
        },
        "status": "working"
    },
    "vehicle_licenses": {
        "licence_plate_number": "",
        "registration_certificate": ""
    },
    "vehicle_specifications": {
        "brand": "",
        "color": "",
        "model": "",
        "transmission": "",
        "vin": "",
        "year": 0
    }
}

data_post = {
    "fields": {
        "account": [
            "balance",
            "balance_limit",
        ],
        "car": [
            "color"
        ],
        "current_status": [
            "status"
        ],
        "driver_profile": [
            "last_name",
            "first_name",
            "phones",
        ],
        "park": [
            "name"
        ]
    },
    "limit": 1000,
    "offset": 0,
    "query": {
        "park": {
            "id": f"{park_id}"
        },
    },
    "sort_order": [
        {
            "direction": "asc",
            "field": "driver_profile.created_date"
        }
    ]
}


@bot.message_handler(['start'])
def start(message):
    bot.clear_step_handler(message)
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Хочу быть авто-курьером', callback_data=f"auto")
    item1 = types.InlineKeyboardButton('Я уже заполнил анкету, хочу зарегестрировать автомобиль', callback_data=f"create")
    markup.add(item)
    markup.add(item1)
    bot.send_message(message.chat.id, 'Обратите внимание! После заполения анкеты вам нужно будет регестрировать свою '
                                      'машину! Подготовьте все нужные документы заранее! Если вы что-то ввели '
                                      'неправльно или хотите вернуться в '
                                      'самое начало, то на каждом этапе есть кнопка "Вернуться в начало", '
                                      'нажимая ее вы начнете вводить все данные сначала! \n Вводите все данные '
                                      'внимательно! \n'
                                      '\n \n Если вы еще не заполняли анкету, то нажимайте на кнопку "Хочу быть '
                                      'авто-курьером"! \n Если вы уже заполнили анкету, то вам необходимо '
                                      'зарегестрировать машину, нажимайте на кнопку "Я уже заполнил анкету, '
                                      'хочу зарегестрировать автомобиль"', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def add_courier(callback):
    req_work_rules = requests.get(url_get_work_rules,
                                  headers={'X-Client-ID': X_Client_id, 'X-API-Key': X_API_Key, 'Accept-Language': 'ru'})

    data_post_auto['account']['work_rule_id'] = req_work_rules.json()['rules'][0]['id']
    data_post_walking['work_rule_id'] = req_work_rules.json()['rules'][0]['id']
    if callback.data == 'auto':
        markup = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
        markup.add(item)
        bot.send_message(callback.message.chat.id, 'Напишите свой номер телефона, начиная с +7', reply_markup=markup)
        bot.register_next_step_handler(callback.message, phone_number_auto)
    # if callback.data == 'walking':
    #     bot.send_message(callback.message.chat.id, 'Напишите свой номер телефона, начиная с +7')
    #     bot.register_next_step_handler(callback.message, phone_number_walking)
    if callback.data == 'restart':
        start(callback.message)
    if callback.data == 'create':
        markup = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
        markup.add(item)
        bot.send_message(callback.message.chat.id, 'Введите свой номер телефона, начиная с +7', reply_markup=markup)
        bot.register_next_step_handler(callback.message, pre_create_car)
    if callback.data == 'restart_create_car':
        create_car(callback.message)
    if callback.data == 'car':
        markup = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
        markup.add(item)
        bot.send_message(callback.message.chat.id,
                         'Введите государственный регистрационный номер вашей машины \nНапример: Т678ВС78',
                         reply_markup=markup)
        bot.register_next_step_handler(callback.message, licence_plate_number)
    if callback.data == 'cargo':
        markup = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
        markup.add(item)
        bot.send_message(callback.message.chat.id,
                         'Введите высоту (в см) вашего ТС. Допустимое значение высоты от 90 до 250 см \nНапример: 200.4',
                         reply_markup=markup)
        bot.register_next_step_handler(callback.message, height)
    if callback.data == 'mech':
        markup = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
        markup.add(item)
        data_post_create_car['vehicle_specifications']['transmission'] = 'mechanical'
        bot.send_message(callback.message.chat.id, 'Введите VIN вашего ТС', reply_markup=markup)
        bot.register_next_step_handler(callback.message, vin)
    if callback.data == 'auto_car':
        markup = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
        markup.add(item)
        data_post_create_car['vehicle_specifications']['transmission'] = 'automatic'
        bot.send_message(callback.message.chat.id, 'Введите VIN вашего ТС', reply_markup=markup)
        bot.register_next_step_handler(callback.message, vin)
    if callback.data == 'robot':
        markup = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
        markup.add(item)
        data_post_create_car['vehicle_specifications']['transmission'] = 'robotic'
        bot.send_message(callback.message.chat.id, 'Введите VIN вашего ТС', reply_markup=markup)
        bot.register_next_step_handler(callback.message, vin)
    if callback.data == 'variator':
        markup = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
        markup.add(item)
        data_post_create_car['vehicle_specifications']['transmission'] = 'variator'
        bot.send_message(callback.message.chat.id, 'Введите VIN вашего ТС', reply_markup=markup)
        bot.register_next_step_handler(callback.message, vin)
    # if callback.data == 'yes':
    #     bot.send_message(callback.message.chat.id, 'Введите название лизинговой компании, у которой вы взяли машину')
    #     bot.register_next_step_handler(callback.message, leasing_company)


#
# def phone_number_walking(message):
#     markup = types.InlineKeyboardMarkup()
#     item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
#     markup.add(item)
#     phone = message.text.strip()
#     data_post_walking['phone'] = phone
#     bot.send_message(message.chat.id,
#                      'Отлично! Теперь введите дату своего рождения в формате дд.мм.гггг \n Например: 11.23.2023',
#                      reply_markup=markup)
#     bot.register_next_step_handler(message, birth_date_walking)
#
#
# def birth_date_walking(message):
#     markup = types.InlineKeyboardMarkup()
#     item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
#     markup.add(item)
#     date = message.text.strip().split('.')
#     data_post_walking['birth_date'] = f'{date[2]}-{date[1]}-{date[0]}'
#     bot.send_message(message.chat.id, 'Введите свое ФИО \n Например: Иванов Иван Иванович', reply_markup=markup)
#     bot.register_next_step_handler(message, full_name_walking)
#
#
# def full_name_walking(message):
#     try:
#         full_name = message.text.strip().split()
#         last_name = full_name[0]
#         first_name = full_name[1]
#         middle_name = full_name[2]
#         data_post_walking['full_name']['last_name'] = last_name
#         data_post_walking['full_name']['first_name'] = first_name
#         data_post_walking['full_name']['middle_name'] = middle_name
#         bot.send_message(message.chat.id, 'Для того чтобы завершить заполнение напишите: "Ок"')
#         bot.register_next_step_handler(message, done_walking)
#     except:
#         bot.send_message(message.chat.id, 'Данные введены неправильно попробуйте ввести сначала')
#         bot.register_next_step_handler(message, full_name_walking)
#
#
# def done_walking(message):
#     print('done')
#     myuuid = str(uuid.uuid4())
#     req = requests.post(url_post_walking,
#                         headers={'X-Idempotency-Token': myuuid, 'X-Park-ID': park_id, 'X-Client-ID': X_Client_id,
#                                  'X-API-Key': X_API_Key},
#                         data=json.dumps(data_post_walking))
#     response = req.json()
#     print(response)
#     if 'contractor_profile_id' in response:
#         bot.send_message(message.chat.id, 'Вы успешно зарегестрировались в парк')
#     if 'code' in response:
#         bot.send_message(message.chat.id,
#                          f'Вы ввели какие-то данные неправильно либо что-то пошло не так, напишите /start и попробуйте начать сначала')
#     print(response["code"], response["message"])


def phone_number_auto(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    phone = message.text.strip()
    req = requests.post(url,
                        headers={'X-Client-ID': X_Client_id, 'X-API-Key': X_API_Key, 'Accept-Language': 'ru'},
                        data=json.dumps(data_post))

    response = req.json()
    for i in response['driver_profiles']:
        if phone in i['driver_profile']['phones']:
            bot.send_message(message.chat.id, 'Такой номер уже зарегестрирован, попробуйте ввести другой', reply_markup=markup)
            bot.register_next_step_handler(message, phone_number_auto)
            break
    else:
        data_post_auto['person']['contact_info']['phone'] = phone
        bot.send_message(message.chat.id,
                         'Отлично! Теперь введите трехбуквенный код страны, в которой получили водительское удостоверение \n Например, код для России: rus',
                         reply_markup=markup)
        bot.register_next_step_handler(message, country_code_auto)


def country_code_auto(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    country_code = message.text.strip().lower()
    data_post_auto['person']['driver_license']['country'] = country_code
    bot.send_message(message.chat.id,
                     'Введите дату окончания действия водительского удостоверения в формате дд.мм.гггг \n Например: 11.23.2023',
                     reply_markup=markup)
    bot.register_next_step_handler(message, expiry_date_auto)


def expiry_date_auto(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    expiry_date = message.text.strip().split('.')
    data_post_auto['person']['driver_license']['expiry_date'] = f'{expiry_date[2]}-{expiry_date[1]}-{expiry_date[0]}'
    bot.send_message(message.chat.id,
                     'Введите дату выдачи водительского удостоверения в формате дд.мм.гггг \n Например: 11.23.2023',
                     reply_markup=markup)
    bot.register_next_step_handler(message, issue_date_auto)


def issue_date_auto(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    issue_date = message.text.strip().split('.')
    data_post_auto['person']['driver_license']['issue_date'] = f'{issue_date[2]}-{issue_date[1]}-{issue_date[0]}'
    bot.send_message(message.chat.id, 'Введите серию и номер водительского удостоверения', reply_markup=markup)
    bot.register_next_step_handler(message, number_auto)


def number_auto(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    number = message.text.strip()
    data_post_auto['person']['driver_license']['number'] = number
    bot.send_message(message.chat.id,
                     'Введите дату начала вашего водительского стажа в формате дд.мм.гггг \n Например: 11.23.2023',
                     reply_markup=markup)
    bot.register_next_step_handler(message, exp_auto)


def exp_auto(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    exp = message.text.strip().split('.')
    data_post_auto['person']['driver_license_experience']['total_since_date'] = f'{exp[2]}-{exp[1]}-{exp[0]}'
    bot.send_message(message.chat.id, 'Введите свое ФИО \n Например: Иванов Иван Иванович', reply_markup=markup)
    bot.register_next_step_handler(message, full_name_auto)


def full_name_auto(message):
    try:
        full_name = message.text.strip().split()
        last_name = full_name[0]
        first_name = full_name[1]
        middle_name = full_name[2]
        data_post_auto['person']['full_name']['last_name'] = last_name
        data_post_auto['person']['full_name']['first_name'] = first_name
        data_post_auto['person']['full_name']['middle_name'] = middle_name
        bot.register_next_step_handler(message, done_auto)
        bot.send_message(message.chat.id, 'Для того чтобы завершить заполнение напишите: "Ок"')
    except:
        bot.send_message(message.chat.id, 'Вы неправльно ввели свое ФИО, попробуйте снова')
        bot.register_next_step_handler(message, full_name_auto)


def done_auto(message):
    myuuid = str(uuid.uuid4())
    req = requests.post(url_post_auto,
                        headers={'X-Idempotency-Token': myuuid, 'X-Park-ID': park_id, 'X-Client-ID': X_Client_id,
                                 'X-API-Key': X_API_Key},
                        data=json.dumps(data_post_auto))
    response = req.json()

    print(response)
    if 'contractor_profile_id' in response:
        markup = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton('Продолжить', callback_data="restart")
        markup.add(item)
        driver['driver_id'] = response['contractor_profile_id']
        bot.send_message(message.chat.id, 'Отлично! Теперь вам необходимо зарегестрировать свою машину. Для '
                                          'продолжения нажмите на кнопку', reply_markup=markup)
    if 'code' in response:
        markup = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
        markup.add(item)
        bot.send_message(message.chat.id, f'Что-то пошло не так, нажмите на кнопку и попробуйте начать сначала',
                         reply_markup=markup)


def pre_create_car(message):
    phone = message.text.strip()
    req = requests.post(url,
                        headers={'X-Client-ID': X_Client_id, 'X-API-Key': X_API_Key, 'Accept-Language': 'ru'},
                        data=json.dumps(data_post))

    response = req.json()
    print(response)
    for i in response['driver_profiles']:

        if phone in i['driver_profile']['phones']:

            create_car(message)
            break
    else:
        markup = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton('Начать регистрацию', callback_data="restart")
        markup.add(item)
        bot.send_message(message.chat.id,
                         'Такого номера не существует \n Попробуйте ввести номер еще раз или нажмите на кнопку, '
                         'чтобы начать заполнять анкету', reply_markup=markup)


def create_car(message):
    bot.clear_step_handler(message)
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Легковой автомобиль', callback_data="car")
    item1 = types.InlineKeyboardButton('Грузовой автомобиль', callback_data="cargo")
    item2 = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")

    markup.add(item)
    markup.add(item1)
    markup.add(item2)
    bot.send_message(message.chat.id, 'Выберите тип вашей машины', reply_markup=markup)


# def leasing_company(message):
#     company = message.text.strip()
#     data_post_create_car['park_profile']['leasing_conditions']['company'] = company
#     bot.send_message(message.chat.id, 'Введите процентную ставку лизинга \nНапример: 11.7')
#     bot.register_next_step_handler(message, leasing_interest_rate)
#
# def leasing_interest_rate(message):
#     procent = message.text.strip()
#     data_post_create_car['park_profile']['leasing_conditions']['interest_rate'] = procent
#     bot.send_message(message.chat.id, 'Введите сумму ежемесячного платежа')
#     bot.register_next_step_handler(message, leasing_interest_rate)

def height(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    try:
        h = message.text.strip()
        data_post_create_car['cargo']['cargo_hold_dimensions']['height'] = float(h)
        bot.send_message(message.chat.id,
                         'Введите длину (в см) вашего ТС. Допустимое значение длины от 170 до 601 см \nНапример: 200.4',
                         reply_markup=markup)
        bot.register_next_step_handler(message, length)
    except:
        bot.send_message(message.chat.id, 'Вы неправильно ввели высоту вашего автомобиля, попробуйте ввести ее заново')
        bot.register_next_step_handler(message, height)


def length(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    try:
        h = message.text.strip()
        data_post_create_car['cargo']['cargo_hold_dimensions']['length'] = float(h)
        bot.send_message(message.chat.id,
                         'Введите ширину (в см) вашего ТС. Допустимое значение ширины от 96 до 250 см \nНапример: 200.4',
                         reply_markup=markup)
        bot.register_next_step_handler(message, width)
    except:
        bot.send_message(message.chat.id, 'Вы неправильно ввели длину вашего автомобиля, попробуйте ввести ее заново')
        bot.register_next_step_handler(message, length)


def width(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    try:
        h = message.text.strip()
        data_post_create_car['cargo']['cargo_hold_dimensions']['width'] = float(h)
        bot.send_message(message.chat.id,
                         'Введите государственный регистрационный номер вашей машины \nНапример: Т678ВС78Э',
                         reply_markup=markup)
        bot.register_next_step_handler(message, licence_plate_number)
    except:
        bot.send_message(message.chat.id, 'Вы неправильно ввели ширину вашего автомобиля, попробуйте ввести ее заново')
        bot.register_next_step_handler(message, width)


def licence_plate_number(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    number = message.text.strip()
    data_post_create_car['vehicle_licenses']['licence_plate_number'] = number
    bot.send_message(message.chat.id, 'Введите номер свидетельства о регистрации ТС', reply_markup=markup)
    bot.register_next_step_handler(message, registration_certificate)


def registration_certificate(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    number = message.text.strip()
    data_post_create_car['vehicle_licenses']['registration_certificate'] = number
    data_post_create_car['park_profile']['callsign'] = number
    bot.send_message(message.chat.id, 'Введите марку вашего ТС \nНапример: Hyundai', reply_markup=markup)
    bot.register_next_step_handler(message, brand)


def brand(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    brand_car = message.text.strip()
    data_post_create_car['vehicle_specifications']['brand'] = brand_car
    bot.send_message(message.chat.id, 'Введите цвет вашего ТС \nНапример: Белый, Желтый, Бежевый, Черный, Голубой, '
                                      'Серый, Красный, Оранжевый, Синий, Зеленый, Коричневый, Фиолетовый, Розовый',
                     reply_markup=markup)
    bot.register_next_step_handler(message, color)


def color(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    color_car = message.text.strip()
    data_post_create_car['vehicle_specifications']['color'] = color_car
    bot.send_message(message.chat.id, 'Введите модель вашего ТС \nНапример: Solaris', reply_markup=markup)
    bot.register_next_step_handler(message, model)


def model(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Механика', callback_data="mech")
    item1 = types.InlineKeyboardButton('Автомат', callback_data="auto_car")
    item2 = types.InlineKeyboardButton('Робот', callback_data="robot")
    item3 = types.InlineKeyboardButton('Вариатор', callback_data="variator")
    item4 = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    markup.add(item4)
    model_car = message.text.strip()
    data_post_create_car['vehicle_specifications']['model'] = model_car
    bot.send_message(message.chat.id, 'Выберите тип коробки передач вашего ТС', reply_markup=markup)


def vin(message):
    markup = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
    markup.add(item)
    vin_num = message.text.strip()
    data_post_create_car['vehicle_specifications']['vin'] = vin_num
    bot.send_message(message.chat.id, 'Введите год выпуска вашего ТС \nНапример: 2019', reply_markup=markup)
    bot.register_next_step_handler(message, year)


def year(message):
    year_car = message.text.strip()
    data_post_create_car['vehicle_specifications']['year'] = int(year_car)
    myuuid = str(uuid.uuid4())
    req = requests.post(url_post_create_car,
                        headers={'X-Park-ID': park_id, 'X-Client-ID': X_Client_id,
                                 'X-API-Key': X_API_Key, 'X-Idempotency-Token': myuuid},
                        data=json.dumps(data_post_create_car))
    response = req.json()
    print(response)
    if 'vehicle_id' in response:
        req_put = requests.put(
            f'https://fleet-api.taxi.yandex.net/v1/parks/driver-profiles/car-bindings?park_id={park_id}&car_id={response["vehicle_id"]}&driver_profile_id={driver["driver_id"]}')
        res = req_put.json()
        if 'code' in res:
            markup = types.InlineKeyboardMarkup()
            item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
            markup.add(item)
            bot.send_message(message.chat.id, f'Что-то пошло не так, нажмите на кнопку и попробуйте начать сначала',
                             reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Поздравляем! Вы успешно зарегестрировались в парк и привязали машину')
    if 'code' in response:
        markup = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton('Вернуться в начало', callback_data="restart")
        markup.add(item)
        bot.send_message(message.chat.id, f'Что-то пошло не так, нажмите на кнопку и попробуйте начать сначала',
                         reply_markup=markup)


bot.infinity_polling()
