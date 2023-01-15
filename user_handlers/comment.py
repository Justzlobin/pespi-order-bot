from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher
from create_bot import dp
from keyboards import *
from states.comment_states import CommentToOrder
from delete.delete_message import UnMessage

delete_message = UnMessage()


async def comment(query: types.CallbackQuery):
    await CommentToOrder.write_comment.set()
    delete_message.add(message_id=await dp.bot.send_message(chat_id=query.message.chat.id,
                                                            text='Введіть примітку.\n'
                                                                 'Приклад:\n'
                                                                 '"Штрих" - штрихкоди\n'
                                                                 '"Серт" - сертифікат\n'
                                                                 '"ттн" - товаро-транспортна накладна\n',
                                                            reply_markup=cancel_state()),
                       chat_id=query.message.chat.id)
    await query.message.delete()


async def stop_comment(query: types.CallbackQuery, state: FSMContext):
    current_state = state.get_state()
    if current_state is None:
        return
    await state.finish()
    await delete_message.destr(query.message.chat.id).delete()
    await query.bot.send_message(text='Дію скасовано!', reply_markup=order_menu_kb(),
                                 chat_id=query.message.chat.id)


async def write_comment(message: types.Message, state: FSMContext):
    async with state.proxy() as data_comment:
        data_comment['comment'] = message.text
        print(tuple(data_comment.values()))
    await sqlite_db.update_comment(message.from_user.id, state)
    await state.finish()
    await delete_message.destr(message.chat.id).delete()
    await message.delete()
    await message.answer(text='Примітка збережена!', reply_markup=order_menu_kb())


def comment_order_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(comment, Cat_KB.filter(action='comment'), state=None)
    dp.register_callback_query_handler(stop_comment, Cat_KB.filter(action='stop_comment'), state='*')
    dp.register_message_handler(write_comment, state=CommentToOrder.write_comment)
    dp.register_callback_query_handler(stop_comment, Cat_KB.filter(action='stop_comment'), state='*')
