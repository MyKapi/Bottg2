import os
import openai
import telebot

print('Бот запущен!')

openai.api_key = "sk- pN2iY juO8BcqUiwxk59eT3BlbkFJ71zSEjyefSrVwBaj"  #  Замените на свой ключ API от OpenAI
bot = telebot.TeleBot('1360739424:AAGR1DMqLxrqxFWJewwI2A9mGwGHuTx-0bE')  # Замените на свой токен бота

if not os.path.exists("users"):
    os.mkdir("users")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Отвечаем на команду /start
    response_text = (
        "Привет! Я бот, обученный на модели GPT-3.5 turbo.\n"
        "Просто отправьте мне сообщение, и я постараюсь ответить на него!"
    )
    bot.send_message(chat_id=message.chat.id, text=response_text)

@bot.message_handler(commands=['help'])
def send_help(message):
    response_text = (
        "/start - Начать общение\n"
        "/clear - Очистить историю сообщений\n"
        "/random - Получить случайный ответ или факт от бота\n"
        "/joke - Получить случайную шутку или анекдот от бота"
    )
    bot.send_message(chat_id=message.chat.id, text=response_text)

# Добавляем команду /reset для полного сброса контекста

@bot.message_handler(commands=['random'])
def send_random(message):
    try:
        send_message = bot.send_message(chat_id=message.chat.id, text='Запрашиваю случайный факт, подождите...')

        # Запрос случайного факта у GPT
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {"role": "user", "content": "Скажи мне случайный факт!"}
            ],
            presence_penalty=0.6
        )

        fact = completion.choices[0].message["content"]
        bot.edit_message_text(
            text=fact,
            chat_id=message.chat.id,
            message_id=send_message.message_id
        )

    except Exception as e:
        bot.send_message(chat_id=message.chat.id, text=e)

@bot.message_handler(commands=['joke'])
def send_joke(message):
    try:
        send_message = bot.send_message(chat_id=message.chat.id, text='Запрашиваю шутку, подождите...')

        # Запрос шутки у GPT
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "user", "content": "Придумай шутку или анекдот!"}
            ],
            presence_penalty=0.6
        )

        joke = completion.choices[0].message["content"]
        bot.edit_message_text(
            text=joke,
            chat_id=message.chat.id,
            message_id=send_message.message_id
        )

    except Exception as e:
        bot.send_message(chat_id=message.chat.id, text=e)

@bot.message_handler(content_types=['text'])
def msg(message):
    if f"{message.chat.id}.txt" not in os.listdir('users'):
        with open(f"users/{message.chat.id}.txt", "x") as f:
            f.write('')

    with open(f'users/{message.chat.id}.txt', 'r', encoding='utf-8') as file:
        oldmes = file.read()

    if message.text == '/clear':
        with open(f'users/{message.chat.id}.txt', 'w', encoding='utf-8') as file:
            file.write('')
        return bot.send_message(chat_id=message.chat.id, text='История сообщений очищена!')

    try:
        send_message = bot.send_message(chat_id=message.chat.id, text='Обрабатываю запрос, пожалуйста подождите!')
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "user", "content": oldmes},
                {"role": "user", "content": f'Предыдущие сообщения: {oldmes}; Запрос: {message.text}'}
            ],
            presence_penalty=0.6
        )

        bot.edit_message_text(
            text=completion.choices[0].message["content"],
            chat_id=message.chat.id,
            message_id=send_message.message_id
        )

        with open(f'users/{message.chat.id}.txt', 'a+', encoding='utf-8') as file:
            file.write(
                message.text.replace('\n', ' ') + '\n' + completion.choices[0].message["content"].replace('\n', ' ') + '\n'
            )

    except Exception as e:
        bot.send_message(chat_id=message.chat.id, text=e)

bot.infinity_polling()