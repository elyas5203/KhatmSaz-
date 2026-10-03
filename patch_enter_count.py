import re

path = 'src/khatmsaz/bot/handlers/member_commitment.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

pattern = r"async with session_scope\(\) as session:\s*await participation_service\.set_commitment_count\(session, pid, target\)\s*await state\.update_data\(_cwiz_mid=None\)\s*await _mwiz\(message, state, t\(\"commit\.count_saved\", lang, target=target\),\s*reply_markup=commitment_count_log_keyboard\(str\(pid\), lang\)\)"
match = re.search(pattern, content)

if match:
    new_code = """async with session_scope() as session:
        # V2 Redesign: COUNT mode is Numeric Reservation mode (7 days)
        # 1. We record the mode for UX/menus
        await participation_service.set_commitment_count(session, pid, target)
        
        # 2. We create the actual 7-day reservation
        participation = await participation_service.repository.get(session, pid)
        khatm = await khatm_service.get_khatm(session, str(participation.khatm_id))
        
        result = await open_contribution_service.create_reservation(
            session, str(khatm.id), pid, target, khatm.repetition_target
        )
        
        if result is None:
            # Capacity exceeded
            await state.clear()
            await message.answer(t("portions.no_capacity_left", lang))
            return
            
        reservation, created = result
        if not created:
            # They already had one, we can just point them to it
            pass

    await state.update_data(_cwiz_mid=None)
    
    # Render the standard portion_done_keyboard (? ????? ???) for reservations
    from khatmsaz.bot.keyboards import contribute_keyboard
    # Let's create a specific complete_reservation button or reuse the existing one from open_reservations
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="? ????? ???", callback_data=f"complete_reservation:{reservation.id}")
    ]])
    
    # Inform them of the 7-day rule
    await _mwiz(message, state, 
        f"? ??? ??? ({target} ???) ?? ??? ? ??? ???? ??? ???? ??. ?? ???? ?? ????? ????? ???? ??? ?? ?????.",
        reply_markup=markup
    )"""
    content = content[:match.start()] + new_code + content[match.end():]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched enter_count successfully!")
else:
    print("Pattern not found!")
