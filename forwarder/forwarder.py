import asyncio

import requests
from main import log
from config import cfg


class Forwarder:
    def __init__(self, processing_queue: asyncio.Queue):
        '''
        The forwarder class will take an asyncio queue as a parameter; the forward_request
        method will pull an item from the queue, build a new payload from
        said item and forward it to QPM.

        :param processing_queue: asyncio.Queue: The processing queue containing modified
        payloads.
        '''
        self.processing_queue = processing_queue

    async def forward_request(self) -> None:
        payload = await self.processing_queue.get()

        new_request = f''
        log.info(f'Forwarding request: {new_request}')

        try:
            response = requests.get(new_request)
            log.info(f'Status code: {response.status_code}\nContent: {response.content}')

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
            requests.exceptions.Timeout
        ) as e:
            log.error(f'Unable to forward request: {e}')

        self.processing_queue.task_done()
