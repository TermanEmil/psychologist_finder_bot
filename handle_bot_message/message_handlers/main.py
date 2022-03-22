import re
import sys

import telegram
from telegram import ReplyKeyboardMarkup, Message, KeyboardButton
from telegram.error import Unauthorized, BadRequest

from Form import update_form, Form, find_form, delete_form
from SubmittedForm import SubmittedForm, save_submission
from spreadsheets import add_to_spreadsheet
from telegram_bot import get_bot


def handle_message(update: telegram.Update):
    try:
        handle_core(update)
    except Unauthorized as e:
        print(f"Unauthorized: {e}", file=sys.stderr)
    except BadRequest as e:
        print(f"Bad request: {e}", file=sys.stderr)


def handle_core(update: telegram.Update):
    message = update.message

    if message.from_user is None or message.from_user.is_bot:
        return

    print(f"Handling message from chat_id: {message.chat_id}")

    if message.text == '/start':
        handle_start(message.chat_id)
        request_person_type(message.chat_id)
        return

    form = find_form(message.chat_id)
    if form is None:
        request_to_start_a_forum(message.chat_id)
        return

    if form.stage == 0:
        if handle_who_i_am(form, message):
            request_name(message.chat_id)
            return

    if form.stage == 1:
        if handle_my_name(form, message):
            request_age(message.chat_id)
            return

    if form.stage == 2:
        if handle_age(form, message):
            request_contact_means(message.chat_id)
            return

    if form.stage == 3:
        if handle_contact_means(form, message):
            request_contact(form)
            return

    if form.stage == 4:
        if handle_contact(form, message):
            request_form_submission(form)
            return

    if form.stage == 5:
        if handle_form_submission(form, message):
            request_to_submit_another_form(form.chat_id)
            return


def request_to_start_a_forum(chat_id: int):
    markup = ReplyKeyboardMarkup([['/start']], one_time_keyboard=True, resize_keyboard=True)
    get_bot().send_message(
        chat_id,
        'Нажмите /start чтобы заполнить форму',
        reply_markup=markup)


def handle_start(chat_id: int):
    update_form(Form(chat_id=chat_id))


person_types = ['Мешканець/ка мiста', 'Психолог']


def request_person_type(chat_id: int):
    markup = ReplyKeyboardMarkup([person_types], one_time_keyboard=True, resize_keyboard=True)
    get_bot().send_message(chat_id, 'Хто ви?', reply_markup=markup)


def handle_who_i_am(form: Form, message: Message):
    if not validate_message_text(message):
        request_person_type(form.chat_id)
        return False

    form.person_type = message.text
    form.stage += 1
    update_form(form)
    return True


def request_name(chat_id: int):
    get_bot().send_message(chat_id, 'Введiть своє iм’я', reply_markup=None)


def handle_my_name(form: Form, message: Message):
    if not validate_message_text(message, 64):
        return False

    if re.match('[\\\\!|#$%&/()=?»«@£§€{}.-;\'<>_,0123456789]+', message.text):
        get_bot().send_message(message.chat_id, 'Недійсний формат імені')
        return False

    form.name = message.text
    form.stage += 1
    update_form(form)
    return True


def request_age(chat_id: int):
    get_bot().send_message(chat_id, 'Вкажiть ваш вiк', reply_markup=None)


def handle_age(form: Form, message: Message):
    if not validate_message_text(message):
        request_age(message.chat_id)
        return False

    if not message.text.isnumeric():
        get_bot().send_message(message.chat_id, 'Недійсний формат віку')
        return False

    form.age = message.text
    form.stage += 1
    update_form(form)
    return True


contact_means = {
    'phone': 'Телефон',
    'telegram': 'Телеграм',
    'skype': 'Skype',
    'messenger': 'Messenger',
    'whatsApp': 'WhatsApp',
    'other': 'Інші'
}


def request_contact_means(chat_id: int):
    markup = ReplyKeyboardMarkup([list(contact_means.values())], one_time_keyboard=True, resize_keyboard=True)
    get_bot().send_message(chat_id, 'Напишiть найзручніший спосіб зв’язку', reply_markup=markup)


def handle_contact_means(form: Form, message: Message):
    if not validate_message_text(message):
        request_contact_means(message.chat_id)
        return False

    if message.text == contact_means['other']:
        get_bot().send_message(message.chat_id, 'Як ви хочете, щоб з вами зв’язалися?')
        return False

    form.contact_means = message.text
    form.stage += 1
    update_form(form)
    return True


def request_contact(form: Form):
    if form.contact_means == contact_means['telegram']:
        request_telegram_contact(form.chat_id)
    else:
        get_bot().send_message(form.chat_id, f"Введіть ваш {form.contact_means}")


def request_telegram_contact(chat_id: int):
    contact_button = KeyboardButton(text="Поділіться моїм контактом", request_contact=True)
    markup = ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True, resize_keyboard=True)
    get_bot().send_message(chat_id, 'Поділіться моїм контактом', reply_markup=markup)


def handle_contact(form: Form, message: Message):
    if message.contact or validate_message_text(message):
        if message.contact:
            contact = message.contact.phone_number
        else:
            contact = message.text

        form.contact = contact
        form.stage += 1
        update_form(form)
        return True

    request_contact(form)
    return False


def request_form_submission(form: Form):
    markup = ReplyKeyboardMarkup([['Отправить', 'Отмена']], one_time_keyboard=True, resize_keyboard=True)
    contact = form.contact.replace('+', "\\+")
    get_bot().send_message(
        form.chat_id,
        f"__{form.name}__ {form.age} років: _{form.person_type}_\n" +
        f"Спосіб зв’язку: _{form.contact_means} {contact}_\n" +
        f"Отправить?",
        reply_markup=markup,
        parse_mode='MarkdownV2')


def handle_form_submission(form: Form, message: Message):
    if message.text not in ['Отправить', 'Отмена']:
        request_form_submission(form)
        return False

    if message.text == 'Отмена':
        get_bot().send_message(form.chat_id, 'Отменено')
    elif message.text == 'Отправить':
        submission = submit_form(form)
        add_to_spreadsheet(submission)
        get_bot().send_message(form.chat_id, 'Спасибо за информацию')

    delete_form(form)
    return True


def submit_form(form: Form):
    submission = SubmittedForm(
        chat_id=form.chat_id,
        person_type=form.person_type,
        name=form.name,
        age=form.age,
        contact_means=form.contact_means,
        contact=form.contact)

    save_submission(submission)
    return submission


def request_to_submit_another_form(chat_id):
    markup = ReplyKeyboardMarkup([['/start']], one_time_keyboard=True, resize_keyboard=True)
    get_bot().send_message(
        chat_id,
        'Заповнити форму ще раз?',
        reply_markup=markup)


def validate_message_text(message: Message, max_size: int = 64):
    if message.text is None:
        get_bot().send_message(message.chat_id, 'Текст не обнаружен')
        request_name(message.chat_id)
        return False

    if len(message.text) > max_size:
        get_bot().send_message(message.chat_id, f"Сообщение не может превышать {max_size} символов")
        return False

    return True
