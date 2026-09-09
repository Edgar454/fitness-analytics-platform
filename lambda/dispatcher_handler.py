# handler.py

import asyncio

from ingestion.src.ingestion.dispatcher.dispatcher import dispatch


def lambda_handler(event, context):
    asyncio.run(dispatch())


    