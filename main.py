import asyncio
import logging
import os
from datetime import datetime

from dotenv import load_dotenv

from bot_globals import client, logger
from database import init_mongodb_conn
from utils.message_scheduler import send_daily_question_and_update_stats
from utils.ratings import read_ratings_txt

load_dotenv()


@client.event
async def on_ready() -> None:
    logger.info("file: main.py ~ on_ready ~ %s",
                datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
    logger.info("file: main.py ~ logged in as a bot %s", client.user)
    server_ids = [guild.id for guild in client.guilds]
    logger.info('file: main.py ~ server IDs: %s', server_ids)

    try:
        synced = await client.tree.sync()
        logger.info("file: main.py ~ synced %s commands", len(synced))

        if os.environ["UPDATE_STATS_ON_START"] == "True":
            daily_reset = os.environ["DAILY_RESET"] == "True"
            weekly_reset = os.environ["WEEKLY_RESET"] == "True"

            await send_daily_question_and_update_stats(True, daily_reset, weekly_reset)
        else:
            await send_daily_question_and_update_stats()

    except Exception as e:
        logger.exception("file: main.py ~ on_ready ~ exception: %s", e)


async def load_extensions() -> None:
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await client.load_extension(f"cogs.{filename[:-3]}")


async def main(token: str) -> None:
    async with client:
        await read_ratings_txt()
        await init_mongodb_conn()
        await load_extensions()
        await client.start(token)


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logger.info("Logger is in INFO mode")

    token = os.environ['TOKEN']

    asyncio.run(main(token))
