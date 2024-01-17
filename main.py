import random
import time
from aiogram import Bot, Dispatcher, F
import asyncio
import os
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
import keyboards
import states
import db_api
VIDEO_ID = None

TOKEN = '6337362490:AAHhSiWLamaeUB5Cc4Jk2mVMmt4xMDwfOxI'

bot = Bot(TOKEN)
dp = Dispatcher()
PASSWORD = '123'
IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'images')
COOLDOWN = 4 * 60 * 60
PLAYERS_WAIT = set()


@dp.message(Command('start'))
async def start(message: Message):
    db_api.add_user(message.chat.id)
    album_builder = MediaGroupBuilder(
        caption="My bot helps my subscribers earn 1 million rupees every day!"
    )
    for i in range(1, 4):
        album_builder.add_photo(
            media=FSInputFile(os.path.join(IMAGE_PATH, f"img{i}.png"))
        )
    await message.answer_media_group(
        media=album_builder.build()
    )

    await asyncio.sleep(2)
    await message.answer('For the bot to work, you need to top up your balance with 1000 rupees.'
                         ' Click start to start earning!', reply_markup=keyboards.start())


@dp.callback_query(F.data == 'start')
async def video_bot(call: CallbackQuery):
    global VIDEO_ID
    if not VIDEO_ID:
        msg = await call.message.answer_video(FSInputFile('IMG_3900.MOV'), reply_markup=keyboards.try_bot())
        VIDEO_ID = msg.video.file_id
    else:
        await call.message.answer_video(VIDEO_ID, reply_markup=keyboards.try_bot())


@dp.callback_query(F.data == 'try_now')
async def try_now(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Enter password")
    await state.set_state(states.EnterPassword.enter_password)


@dp.message(states.EnterPassword.enter_password)
async def check_password(message: Message, state: FSMContext):
    if message.text == PASSWORD:
        await state.clear()
        return await message.answer('Start earning 5000 rupees per day!', reply_markup=keyboards.earn_money())

    await message.answer("Invalid password\nEnter again")


@dp.callback_query(F.data == 'get_signal')
async def get_signal(call: CallbackQuery):
    if call.message.chat.id in PLAYERS_WAIT:
        return

    user = db_api.get_user(call.message.chat.id)
    if (user[1] >= 20) and (time.time() - user[2] < COOLDOWN):
        return await call.message.answer(
            '⚠️The CASINO system, noticed suspicious!⚠️\n\n'
            '🛑Signals are limited to 4 hours!🛑\n\n'
            '🟢Make a deposit 400 rupees to continue receiving signals!🟢\n\n'
            'Or wait for 4 hours - the bot will restore the work, so as not to arouse suspicion of CASINO⚠️',
            reply_markup=keyboards.get_me()
        )

    tries = user[1]
    if tries >= 20:
        db_api.update_tries(call.message.chat.id, 0)
        tries = 0

    PLAYERS_WAIT.add(call.message.chat.id)
    await call.message.answer('Checking bets🚀')
    await asyncio.sleep(random.randint(1, 3))

    await call.message.answer(
        f'PLAYER: @{call.message.from_user.username}\n'
        f'*CASHOUT: %.2f ✅*' % round(random.randint(100, 250)/100, 2),
        parse_mode='markdown',
        reply_markup=keyboards.get_next_signals()
    )

    PLAYERS_WAIT.remove(call.message.chat.id)
    db_api.update_timestamp_user(call.message.chat.id)
    db_api.update_tries(call.message.chat.id, tries+1)


asyncio.run(dp.start_polling(bot))
