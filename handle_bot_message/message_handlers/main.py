import re
import sys

from telegram import ReplyKeyboardMarkup, Message, KeyboardButton, Update
from telegram.error import Forbidden, BadRequest
from telegram.ext import ContextTypes

from Form import update_form, Form, find_form, delete_form
from SubmittedForm import SubmittedForm, save_submission
from consts import person_types, patient_type, psychologist_type

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update is None or update.message is None:
        return

    if update.message.from_user is None or update.message.from_user.is_bot:
        return

    try:
        await handle_core(update)
    except Forbidden as e:
        print(f"Unauthorized: {e}", file=sys.stderr)
    except BadRequest as e:
        print(f"Bad request: {e}", file=sys.stderr)


async def handle_core(update: Update):
    message = update.message

    print(f"Handling message from chat_id: {message.chat_id}")

    if message.text == '/start':
        handle_start(message.chat_id)
        await request_person_type(update)
        return

    form = find_form(message.chat_id)
    if form is None:
        await request_to_start_a_forum(update)
        return

    if form.stage == 0:
        if await handle_who_i_am(form, update):
            await request_name(update.message)
            return

    if form.stage == 1:
        if await handle_my_name(form, message):
            await request_age(message)
            return

    if form.stage == 2:
        if await handle_age(form, message):
            await request_contact_means(message)
            return

    if form.stage == 3:
        if await handle_contact_means(form, message):
            await request_contact(form, message)
            return

    if form.stage == 4:
        if await handle_contact(form, message):
            if await request_consultation_preference(form, message):
                return

    if form.stage == 5:
        if await handle_consultation_preference(form, message):
            await request_form_submission(form, message)
            return

    if form.stage == 6:
        if await handle_form_submission(form, message):
            await request_to_submit_another_form(message)
            return


async def request_to_start_a_forum(update: Update):
    markup = ReplyKeyboardMarkup([['/start']], one_time_keyboard=True, resize_keyboard=True)
    press_start_to_fill_the_form = 'Нажмите /start чтобы заполнить форму'
    await update.message.reply_text(press_start_to_fill_the_form, reply_markup=markup)


def handle_start(chat_id: int):
    update_form(Form(chat_id=chat_id))


async def request_person_type(update: Update):
    markup = ReplyKeyboardMarkup([person_types], one_time_keyboard=True, resize_keyboard=True)
    who_are_you = 'Хто ви?'
    await update.message.reply_text(who_are_you, reply_markup=markup)


async def handle_who_i_am(form: Form, update: Update):
    if not validate_message_text(update.message):
        await request_person_type(update)
        return False

    if update.message.text not in person_types:
        await update.message.reply_text(f"{patient_type} чи {psychologist_type}?", reply_markup=None)
        await request_person_type(update)
        return False

    form.person_type = update.message.text
    form.stage += 1
    update_form(form)
    return True


async def request_name(message: Message):
    enter_your_name = 'Введiть своє iм’я'
    await message.reply_text(enter_your_name, reply_markup=None)


async def handle_my_name(form: Form, message: Message):
    if not await validate_message_text(message, 64):
        return False

    if re.match('[\\\\!|#$%&/()=?»«@£§€{}.-;\'<>_,0123456789]+', message.text):
        invalid_name_format = 'Недійсний формат імені'
        await message.reply_text(invalid_name_format)
        return False

    form.name = message.text
    form.stage += 1
    update_form(form)
    return True


async def request_age(message: Message):
    enter_your_age = 'Вкажiть ваш вiк'
    await message.reply_text(enter_your_age, reply_markup=None)


async def handle_age(form: Form, message: Message):
    if not await validate_message_text(message):
        await request_age(message)
        return False

    if not message.text.isnumeric():
        invalid_age_format = 'Недійсний формат віку'
        await message.reply_text(invalid_age_format)
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


async def request_contact_means(message: Message):
    markup = ReplyKeyboardMarkup([list(contact_means.values())], one_time_keyboard=True, resize_keyboard=True)
    enter_a_way_to_contact_you = 'Напишiть найзручніший спосіб зв’язку'
    await message.reply_text(enter_a_way_to_contact_you, reply_markup=markup)


async def handle_contact_means(form: Form, message: Message):
    if not await validate_message_text(message):
        await request_contact_means(message)
        return False

    if message.text == contact_means['other']:
        how_would_you_like_to_be_contacted = 'Як ви хочете, щоб з вами зв’язалися?'
        await message.reply_text(how_would_you_like_to_be_contacted)
        return False

    form.contact_means = message.text
    form.stage += 1
    update_form(form)
    return True


async def request_contact(form: Form, message: Message):
    if form.contact_means == contact_means['telegram']:
        await request_telegram_contact(message)
    else:
        enter_your_contact_means = f"Введіть ваш {form.contact_means}"
        await message.reply_text(enter_your_contact_means)


async def request_telegram_contact(message: Message):
    send_my_telegram_contact = 'Поділіться моїм контактом'
    contact_button = KeyboardButton(text=send_my_telegram_contact, request_contact=True)
    markup = ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True, resize_keyboard=True)
    await message.reply_text(send_my_telegram_contact, reply_markup=markup)


async def handle_contact(form: Form, message: Message):
    if message.contact or await validate_message_text(message):
        if message.contact:
            contact = message.contact.phone_number
        else:
            contact = message.text

        form.contact = contact
        form.stage += 1
        update_form(form)
        return True

    await request_contact(form, message)
    return False


consultation_preferences = ['Чоловік', 'Жінка', 'Без різниці']


async def request_consultation_preference(form: Form, message: Message):
    if form.person_type == psychologist_type:
        return False

    markup = ReplyKeyboardMarkup([[*consultation_preferences]], one_time_keyboard=True, resize_keyboard=True)
    do_you_have_preferences_for_therapist_gender = 'Чи є побажання щодо статi терапевта?'
    await message.reply_text(do_you_have_preferences_for_therapist_gender, reply_markup=markup)
    return True


async def handle_consultation_preference(form: Form, message: Message):
    if form.person_type == psychologist_type:
        form.stage += 1
        update_form(form)
        return True

    if not await validate_message_text(message) or message.text not in consultation_preferences:
        await request_consultation_preference(form, message)
        return False

    if message.text in consultation_preferences[0:2]:
        form.consultation_preference = message.text

    form.stage += 1
    update_form(form)


async def request_form_submission(form: Form, message: Message):
    markup = ReplyKeyboardMarkup([['Отправить', 'Отмена']], one_time_keyboard=True, resize_keyboard=True)
    contact = form.contact.replace('+', "\\+")

    if form.consultation_preference is None:
        consultation_preference = ''
    else:
        consultation_preference = f"Cтать терапевта: _{form.consultation_preference}_\n"

    await message.reply_text(
        f"__{form.name}__ {form.age} років: _{form.person_type}_\n" +
        f"Спосіб зв’язку: _{form.contact_means} {contact}_\n" +
        consultation_preference +
        f"Отправить?",
        reply_markup=markup,
        parse_mode='MarkdownV2')


async def handle_form_submission(form: Form, message: Message):
    from spreadsheets import add_to_spreadsheet

    if message.text not in ['Отправить', 'Отмена']:
        await request_form_submission(form, message)
        return False

    if message.text == 'Отмена':
        await message.reply_text('Отменено')
    elif message.text == 'Отправить':
        submission = submit_form(form)
        add_to_spreadsheet(submission)
        await message.reply_text('Спасибо за информацию')

    delete_form(form)
    return True


def submit_form(form: Form):
    submission = SubmittedForm(
        chat_id=form.chat_id,
        person_type=form.person_type,
        name=form.name,
        age=form.age,
        contact_means=form.contact_means,
        contact=form.contact,
        consultation_preference=form.consultation_preference)

    save_submission(submission)
    return submission


async def request_to_submit_another_form(message: Message):
    markup = ReplyKeyboardMarkup([['/start']], one_time_keyboard=True, resize_keyboard=True)
    await message.reply_text('Заповнити форму ще раз?', reply_markup=markup)


async def validate_message_text(message: Message, max_size: int = 64):
    if message.text is None:
        no_text_detected = 'Текст не обнаружен'
        await message.reply_text(no_text_detected)
        await request_name(message)
        return False

    if len(message.text) > max_size:
        await message.reply_text(f"Сообщение не может превышать {max_size} символов")
        return False

    return True
