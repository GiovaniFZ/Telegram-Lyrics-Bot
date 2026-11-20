from services import BotService, OSService

async def donation_command(
    bot_service: BotService,
    os_service: OSService,
    update,
    _context,
):
    usdt_key = os_service.getEnv("USDT_KEY")
    btc_key = os_service.getEnv("BTC_KEY")
    await bot_service.send_message(
        update,
        "*Any help is welcome to help in Song Lyrics Bot development! Here is how you can donate:*\n\n"
        "• [Buy me a coffee](https://buymeacoffee.com/akaidk)\n"
        "• [Livepix](https://livepix.gg/akaidk)\n"
        f"*• USDT/ETH*: `{usdt_key}`\n"
        f"*• BTC*: `{btc_key}`\n\n"
        "*For any other methods, please contact me at @akaidk.*"
        ,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )
    return