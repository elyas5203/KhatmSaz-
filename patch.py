
with open(r'c:\xampp\htdocs\Khatm\src\khatmsaz\bot\handlers\portions.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = '''    if slug is None:
        return
    asset = await content_service.get_devotional_asset(session, slug)
    if asset is None:
        return
    platform: Platform = getattr(message.bot, 'khatmsaz_platform', Platform.TELEGRAM)
    lang = await _lang_for(message.chat.id, message.bot)
    if asset.text_body:
        for chunk in asset.text_body.split('\\x1e'):
            await message.answer(chunk)
    from khatmsaz.bot.handlers.devotional import deliver_devotional_media
    await deliver_devotional_media(session, message, slug=slug, asset=asset, platform=platform, lang=lang)'''

replacement = '''    platform: Platform = getattr(message.bot, 'khatmsaz_platform', Platform.TELEGRAM)
    lang = await _lang_for(message.chat.id, message.bot)

    if category and category.image_url:
        from aiogram.types import URLInputFile
        try:
            await message.answer_photo(URLInputFile(category.image_url))
        except Exception:
            pass # fallback if URL is invalid

    if slug is None:
        if category and category.body_text:
            await message.answer(escape(category.body_text))
        return
        
    asset = await content_service.get_devotional_asset(session, slug)
    if asset is None:
        if category and category.body_text:
            await message.answer(escape(category.body_text))
        return

    if asset.text_body:
        for chunk in asset.text_body.split('\\x1e'):
            await message.answer(chunk)
    elif category and category.body_text:
        await message.answer(escape(category.body_text))

    from khatmsaz.bot.handlers.devotional import deliver_devotional_media
    await deliver_devotional_media(session, message, slug=slug, asset=asset, platform=platform, lang=lang)'''

if target in code:
    with open(r'c:\xampp\htdocs\Khatm\src\khatmsaz\bot\handlers\portions.py', 'w', encoding='utf-8') as f:
        f.write(code.replace(target, replacement))
    print('SUCCESS')
else:
    print('TARGET NOT FOUND')

