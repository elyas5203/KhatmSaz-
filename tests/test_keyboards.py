from uuid import uuid4

from khatmsaz.bot.keyboards import creator_khatm_keyboard


def test_creator_keyboard_callback_data_fit_telegram_limit():
    keyboard = creator_khatm_keyboard(str(uuid4()))
    callback_values = [
        button.callback_data
        for row in keyboard.inline_keyboard
        for button in row
        if button.callback_data is not None
    ]
    assert callback_values
    assert all(len(value.encode("utf-8")) <= 64 for value in callback_values)
