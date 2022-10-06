import logging
import random
from config import TOKEN

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)


# Включим ведение журнала
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем константы этапов разговора
GAME, TOTAL_CANDY, GAME_MOVE, FIRST_MOVE, BOT_PLAY, USER_PLAY = range(
    6)

READY = 'Всегда готов. Вперед!'
RUN_AWAY = 'Не хочу играть, отстань'
YES = 'Да, давай играть. Готов к любому варианту.'
NO = 'Нет, я убегаю...'
YES_KEY = 'Да! Теперь буду я ходить!'
NO_KEY = 'Нет, с меня хватит!'

# функция обратного вызова точки входа в разговор


def start(update, context):
    # Список кнопок для ответа
    reply_keyboard = [[READY], [RUN_AWAY]]
    # Создаем простую клавиатуру для ответа
    markup_key = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=False)
    # Начинаем разговор
    update.message.reply_text(
        f'Привет! Я Умный Бот. Готов поиграть с Вами в игру с конфетами. Краткие правила: На столе лежит определенное число конфет (сколько Вы зададите, но не менее 10). Мы делаем ход друг после друга. Первый ход определяется жеребьёвкой. За один ход можно забрать не более чем определенное число конфет (сколько вы зададите, но не более 1/3 от общего количества). Тот, кто берет последнюю конфету - проиграл.'
        'Команда /stop, чтобы прекратить игру.\n\n'
        'Готовы играть?',
        reply_markup=markup_key)
    context.bot.send_sticker(update.effective_chat.id,
                             'CAACAgIAAxkBAAIJXGM_AAEajJr1qsTmVMOsaQICxcHLNgACuQAD9wLID5Ahqvg5d0bYKgQ')
    # переходим к этапу `GAME`
    return GAME


def game(update, context):
    # определяем пользователя
    user = update.message.from_user
    key = update.message.text
    logger.info("Имя пользователя - Готовность играть: %s - %s",
                user.first_name, update.message.text)
    if key == READY:
        context.bot.send_sticker(update.effective_chat.id,
                                 'CAACAgIAAxkBAAIJYmM_AAGr5dzxmzhrlAUwaYEkp1vSswACmgAD9wLID9HVBvL9etQ4KgQ')
        update.message.reply_text(
            'Отлично, тогда начнем!',
            reply_markup=ReplyKeyboardRemove())
        update.message.reply_text(
            'Напишите, сколько будем разыгрывать конфет: сколько их будет перед началом игры.\n'
            'Отправьте /stop, если передумали играть.\n')
    # переходим к этапу CALC_GAME
        return TOTAL_CANDY
    elif key == RUN_AWAY:
        context.bot.send_sticker(update.effective_chat.id,
                                 'CAACAgIAAxkBAAIJX2M_AAF2ecglXLM2wOmrFUruFCPONwACPQEAAjDUnREQ98oHcZKP7ioE')
        logger.info("Пользователь %s прекратил диалог.", user.first_name)
        update.message.reply_text(
            'Жаль! Возвращайтесь (кнопка /start), буду рад!',
            reply_markup=ReplyKeyboardRemove())
        # context.bot.send_sticker(update.effective_chat.id,
        #                          'CAACAgIAAxkBAAIJX2M_AAF2ecglXLM2wOmrFUruFCPONwACPQEAAjDUnREQ98oHcZKP7ioE')
        return ConversationHandler.END


def sum_total(update, context):
    # определяем пользователя
    user = update.message.from_user
    # Пишем в журнал пол пользователя
    logger.info("Общее число конфет %s: %s",
                user.first_name, update.message.text)
    # Следующее сообщение с удалением клавиатуры `ReplyKeyboardRemove`
    sum_total = update.message.text
    if sum_total.isdigit() == False or int(sum_total) < 10:
        update.message.reply_text(
            'Вы ввели некорректное число конфет. Введите целое число не менее 10.\n'
            'Отправьте /stop, если передумали играть, но в этом случае я расстроюсь.\n'
        )
        context.bot.send_sticker(update.effective_chat.id,
                                 'CAACAgIAAxkBAAIJZWM_AAHiUqDMmRvQyMOca102OwNqGAACSgADUomRIyleaTHC6cM1KgQ')
        return TOTAL_CANDY
    else:
        sum_total = int(sum_total)
        context.user_data['sum_total'] = sum_total
        update.message.reply_text(
            'Введите максимальное число конфет, которое можно брать за один ход игрока (более 1, целое положительное, не более трети общего числа конфет).\n'
            'Отправьте /stop, если передумали играть, но в этом случае я расстроюсь.\n'
        )
        context.bot.send_sticker(update.effective_chat.id,
                                 'CAACAgIAAxkBAAIJXGM_AAEajJr1qsTmVMOsaQICxcHLNgACuQAD9wLID5Ahqvg5d0bYKgQ')
    return GAME_MOVE

# Обрабатываем фотографию пользователя


def game_move(update, context):
    # определяем пользователя
    reply_keyboard = [[YES], [NO]]
    # Создаем простую клавиатуру для ответа
    markup_key = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=False)
    user = update.message.from_user
    logger.info("Максимальное число конфет за один ход игрока %s: %s",
                user.first_name, update.message.text)
    game_move = update.message.text
    sum_total = context.user_data.get('sum_total', 'Not found')
    if game_move.isdigit() == False or int(game_move) < 2:
        update.message.reply_text(
            'Вы указали некорректное число конфет, которое можно брать за один ход.\n'
            'Введите целое число более 1.\n'
            'Отправьте /stop, если передумали играть, но в этом случае я расстроюсь.\n'
        )
        context.bot.send_sticker(update.effective_chat.id,
                                 'CAACAgIAAxkBAAIJZWM_AAHiUqDMmRvQyMOca102OwNqGAACSgADUomRIyleaTHC6cM1KgQ')
        return GAME_MOVE
    elif int(game_move) > int(sum_total/3):
        update.message.reply_text(
            'Вы ввели слишком большое число конфет, которое можно брать за один ход игрока.\n'
            'Введите число поменьше.\n'
            'Отправьте /stop, если передумали играть, но в этом случае я расстроюсь.\n'
        )
        context.bot.send_sticker(update.effective_chat.id,
                                 'CAACAgIAAxkBAAIJXGM_AAEajJr1qsTmVMOsaQICxcHLNgACuQAD9wLID5Ahqvg5d0bYKgQ')
        return GAME_MOVE
    else:
        game_move = int(game_move)
        context.user_data['game_move'] = game_move
        update.message.reply_text(
            'Продолжим - вытянем жребий!\n'
            'Внимание! Барабанная дробь...Сейчас станет известно, кто ходит первым...\n'
            'Отправьте /stop, если передумали играть, но в этом случае я расстроюсь.\n'
        )
        context.bot.send_sticker(update.effective_chat.id,
                                 'CAACAgIAAxkBAAIJbmM_AZy5_Tr12wsHYd9i-JL0qQbdAAIjAAMoD2oUJ1El54wgpAYqBA')
        update.message.reply_text(
            'Готовы увидеть результаты жеребьевки (кто ходит первый)?',
            reply_markup=markup_key)
        return FIRST_MOVE


def get_first_move(update, context):
    # reply_keyboard = [['Хорошо'], ['Отказываюсь продолжать игру']]
    # markup_key = ReplyKeyboardMarkup(
    #     reply_keyboard, one_time_keyboard=False)
    user = update.message.from_user

    first_lot = random.randint(1, 2)
    if first_lot == 1:
        name = 'Умный Бот'
    elif first_lot == 2:
        name = user.first_name
    context.user_data['first_lot'] = first_lot
    decision = update.message.text
    logger.info("Решение игрока увидеть результаты жеребьевки %s: %s",
                user.first_name, update.message.text)
    # print(context.user_data.get('first_lot', 'Not found'))
    logger.info("Кто ходит первый (если 1 - Bot, если 2 - User): %s",
                context.user_data.get('first_lot', 'Not found'))
    if decision == YES:
        update.message.reply_text(
            f'Первым ходит: {name}.', reply_markup=ReplyKeyboardRemove())
        if context.user_data.get('first_lot', 'Not found') == 1:
            context.bot.send_sticker(update.effective_chat.id,
                                     'CAACAgIAAxkBAAIJcWM_AdgJjL4ag0OfpJutr-9gGyv8AAKTAAP3AsgPJeWS_-k7iFUqBA')
            update.message.reply_text(
                'Введите что-нибудь и отправте сообщение! БЫСТРО!')
            return BOT_PLAY
        elif context.user_data.get('first_lot', 'Not found') == 2:
            context.bot.send_sticker(update.effective_chat.id,
                                     'CAACAgIAAxkBAAIJdGM_AiiRHINOTjz0Fq1vxChu9dqxAAJvAAP3AsgP6TP9mweCjjIqBA')
            update.message.reply_text(
                'Введите, сколько конфет будете брать.')
            context.bot.send_sticker(update.effective_chat.id,
                                     'CAACAgIAAxkBAAIJXGM_AAEajJr1qsTmVMOsaQICxcHLNgACuQAD9wLID5Ahqvg5d0bYKgQ')
            return USER_PLAY
    elif decision == NO:
        update.message.reply_text(
            'Я расстроен! Но Ваше решение принимаю... (Команда: /start для новой игры)', reply_markup=ReplyKeyboardRemove())
        context.bot.send_sticker(update.effective_chat.id,
                                 'CAACAgIAAxkBAAIJX2M_AAF2ecglXLM2wOmrFUruFCPONwACPQEAAjDUnREQ98oHcZKP7ioE')
        return ConversationHandler.END


def play_as_bot(update, context):
    print('play_as_bot')
    sum_total = context.user_data.get('sum_total', 'Not found')
    game_move = context.user_data.get('game_move', 'Not found')
    max_count_after_bot = game_move + 2
    logger.info("Шаг бота --- Общее число конфет | Максимальное количество конфет за 1 шаг | Максимальное число конфет, которое должно оставаться после хода бота --- %s| %s| %s",
                context.user_data.get('sum_total', 'Not found'),
                context.user_data.get('game_move', 'Not found'),
                max_count_after_bot)

    if sum_total >= 2*max_count_after_bot:
        step = 1
    elif (sum_total - game_move) > game_move:
        step = 1
    elif sum_total == max_count_after_bot:
        step = 0
        update.message.reply_text(
            f'Извините, я наелся и пропущу 1 ход!')
        context.bot.send_sticker(update.effective_chat.id,
                                 'CAACAgIAAxkBAAIJd2M_AoJ3Dvag7j4lVRhV4BPkuRYPAAJrAAP3AsgPPlPH7DgfmtMqBA')
        update.message.reply_text(
            'Введите, сколько конфет будете брать.')
        context.bot.send_sticker(update.effective_chat.id,
                                 'CAACAgIAAxkBAAIJXGM_AAEajJr1qsTmVMOsaQICxcHLNgACuQAD9wLID5Ahqvg5d0bYKgQ')
        return USER_PLAY
    else:
        if sum_total - 1 > game_move:
            step = 1
        else:
            step = sum_total - 1
    if step > 0:
        update.message.reply_text(
            f'Умный Бот забрал {step} конфет(-у/-ы).')
    else:
        update.message.reply_text(
            f'Умный Бот пропустил ход. Ваша очередь!')
        context.bot.send_sticker(update.effective_chat.id,
                                 'CAACAgIAAxkBAAIJcWM_AdgJjL4ag0OfpJutr-9gGyv8AAKTAAP3AsgPJeWS_-k7iFUqBA')

    sum_total -= int(step)
    context.user_data['sum_total'] = sum_total
    if sum_total == 1:
        update.message.reply_text(
            f'Умный Бот выиграл! Вы проиграли: Вам осталась всего 1 конфета.')
        context.bot.send_sticker(update.effective_chat.id,
                                 'CAACAgIAAxkBAAIJemM_AzyV4r6P55c3aIhJHR8xdkURAAKUAAP3AsgPoua-568NrOgqBA')
        return ConversationHandler.END
    if sum_total > 1:
        update.message.reply_text(
            f'После хода Вашего противника Умного Бота осталось {sum_total} конфет(-а/-ы).')
    update.message.reply_text(
        'Введите, сколько конфет будете брать.')
    context.bot.send_sticker(update.effective_chat.id,
                             'CAACAgIAAxkBAAIJXGM_AAEajJr1qsTmVMOsaQICxcHLNgACuQAD9wLID5Ahqvg5d0bYKgQ')
    return USER_PLAY


def play_as_user(update, context):
    print('play_as_user')
    user = update.message.from_user
    sum_total = context.user_data.get('sum_total', 'Not found')
    game_move = context.user_data.get('game_move', 'Not found')
    step = update.message.text
    update.message.reply_text(
        f'Вы делаете ход... {step} конфет.')
    logger.info("Шаг игрока. Общее число конфет, количество конфет за 1 шаг, число конфет, которое забрал пользователь %s: %s: %s",
                context.user_data.get('sum_total', 'Not found'),
                context.user_data.get('game_move', 'Not found'),
                step)
    if step.isdigit() == False or int(step) < 1 or int(step) > game_move:
        update.message.reply_text(
            f'{user.first_name}, некорректный ход. Должно быть число от 1 до {game_move}.\nОтправьте /stop, если передумали играть, но в этом случае я расстроюсь.')
        context.bot.send_sticker(update.effective_chat.id,
                                 'CAACAgIAAxkBAAIJZWM_AAHiUqDMmRvQyMOca102OwNqGAACSgADUomRIyleaTHC6cM1KgQ')
        return USER_PLAY
    sum_total -= int(step)
    context.user_data['sum_total'] = sum_total
    if sum_total >= 2:
        update.message.reply_text(
            f'После Вашего хода, {user.first_name}, осталось(-лись, -лась) {sum_total} конфет(-ы, -а).\nОтправьте /stop, если передумали играть, но в этом случае я расстроюсь.')
        update.message.reply_text(
            'Введите что-нибудь и отправьте сообщение! БЫСТРО!')
        return BOT_PLAY
    elif sum_total == 1:
        update.message.reply_text(
            f'После Вашего хода, {user.first_name}, осталась {sum_total} конфета.')
        update.message.reply_text(
            f'Вы выиграли! Боту "Умный Бот" досталась последняя конфета. Поздравляем, {user.first_name}! Для начала новой игры нажмите /start')
        context.bot.send_sticker(update.effective_chat.id,
                                 'CAACAgIAAxkBAAIJa2M_AXN31zjSnP4pDq_PJd4cxxu7AAJwDwACOj7BS9IRGlNhXSg3KgQ')
        return ConversationHandler.END


def stop(update, context):
    # определяем пользователя
    user = update.message.from_user
    # Пишем в журнал о том, что пользователь прекращает разговор.
    logger.info("Пользователь %s отменил разговор.", user.first_name)
    # Отвечаем на отказ продолжить диалог.
    update.message.reply_text(
        'Мое дело предложить - Ваше отказаться...\n'
        'Будет скучно - возвращайтесь (команда: /start)!',
        reply_markup=ReplyKeyboardRemove()
    )
    context.bot.send_sticker(update.effective_chat.id,
                             'CAACAgIAAxkBAAIJYmM_AAGr5dzxmzhrlAUwaYEkp1vSswACmgAD9wLID9HVBvL9etQ4KgQ')
    # Заканчиваем разговор.
    return ConversationHandler.END


if __name__ == '__main__':
    # Создаем Updater и передаем ему токен вашего бота.
    updater = Updater(TOKEN)
    # получаем диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Определяем обработчик разговоров `ConversationHandler`
    # с состояниями GAME, TOTAL_CANDY, GAME_MOVE, FIRST_MOVE, BOT_PLAY и USER_PLAY
    conv_handler = ConversationHandler(  # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('stop', stop)
        ],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            GAME: [MessageHandler(Filters.regex('^(Всегда готов. Вперед!|Не хочу играть, отстань)$'), game)],
            TOTAL_CANDY: [MessageHandler(Filters.text & ~Filters.command, sum_total), CommandHandler('stop', stop)],
            GAME_MOVE: [MessageHandler(Filters.text & ~Filters.command, game_move), CommandHandler('stop', stop)],
            FIRST_MOVE: [MessageHandler(Filters.regex('^(Да, давай играть. Готов к любому варианту.|Нет, я убегаю...)$') & ~Filters.command, get_first_move), CommandHandler('stop', stop)],
            BOT_PLAY: [MessageHandler(Filters.text & ~Filters.command, play_as_bot), CommandHandler('stop', stop)],
            USER_PLAY: [MessageHandler(Filters.text & ~Filters.command, play_as_user), CommandHandler('stop', stop)],
        },

        # точка выхода из разговора
        fallbacks=[CommandHandler('stop', stop)],
    )

    # Добавляем обработчик разговоров `conv_handler`
    dispatcher.add_handler(conv_handler)

    # Запуск бота
    updater.start_polling()
    print('server started')
    updater.idle()
    print('server stoped')
