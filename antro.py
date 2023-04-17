import asyncio
import logging
import os
import time

import httpx
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message

TOKEN =  os.getenv('TELEGRAM_TOKEN')
antro_api_key = os.getenv('ANTRO_API_KEY')
permitted_users = list(map(lambda x: int(x) ,os.getenv('PERMITTED_USERS').split(',')))

# All handlers should be attached to the Router (or Dispatcher)
router = Router()


def send_request(prompt):
    data = {
    "prompt": f"\n\nHuman: {prompt}\n\nAssistant: ",
    "model": "claude-v1", "max_tokens_to_sample": 1000, "stop_sequences": ["\n\nHuman:"]
    }
    headers = {
        "x-api-key": antro_api_key,
        "Content-Type": "application/json"
    }

    response = httpx.post("https://api.anthropic.com/v1/complete", json=data, headers=headers, timeout=None)

    if response.status_code != 200:
        logging.error(f"Anthropic API responded with {response.status_code} {response.reason_phrase}")
        return None

    return response.json()

@router.message(Command(commands=["start"]))
async def command_start_handler(message: Message) -> None:
    """
    This handler receive messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")


@router.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward received message back to the sender

    By default, message handler will handle all message types (like text, photo, sticker and etc.)
    """
    try:
        if message.from_user.id in permitted_users:
            # measure time
            start = time.time()
            response = send_request(message.text)
            end = time.time()
            logging.info(f"Time taken: {end - start}")
            completion = response['completion']
            await message.answer(f'<b>{message.text}</b>\n<i>Took {round(end - start)} seconds</i>\n\n{completion}')
        else:
            await message.answer("You are not allowed to use this bot!")
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    # Dispatcher is a root router
    dp = Dispatcher()
    # ... and all other routers should be attached to Dispatcher
    dp.include_router(router)

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode="HTML")
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(permitted_users)
    asyncio.run(main())
