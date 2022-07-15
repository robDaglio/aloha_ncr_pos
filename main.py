# ======================================================================
# Application name: Aloha NCR/POS Date Corrections
# Description: This program acts as a forwarder for POS payloads destined for QPM.
# It will parse the date within the XML payload, compare it to the current date
# and correct it if necessary before forwarding to QPM.
# Author: Rob Daglio
# Repository: http://sckgit.fastinc.com/QPM/aloha-ncr-pos
# ======================================================================

import json
import logging
import sys
import asyncio

from config import cfg
from aiohttp import web

logging.basicConfig(
    format='%(process)d - %(asctime)s - %(funcName)s - %(levelname)s: %(message)s',
    datefmt='%m-%d-%Y %H:%M:%S',
    level=logging.getLevelName(cfg.log_level.upper()),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(cfg.log_file, 'a+', 'utf-8')
    ]
)

log = logging.getLogger()
routes = web.RouteTableDef()


@routes.get('/instore/posXml')
async def handler(request):
    from parser.parser import CorrectDate
    from forwarder.forwarder import Forwarder

    xml_modifier = CorrectDate(request_queue)
    request_forwarder = Forwarder(request_queue)

    logging.info(f'Incoming request on port {cfg.listening_port}.')

    modify_task = asyncio.create_task(xml_modifier.modify_xml(request.query))
    forward_task = asyncio.create_task(request_forwarder.forward_request())

    await asyncio.gather(modify_task, forward_task)
    await request_queue.join()

    for coro in forward_task:
        coro.cancel()

    return web.Response(text='Request processed.')


def read_version_properties(properties_file: str) -> str:
    try:
        with open(properties_file, 'r') as f:
            version = f.read()
            return version.split('=')[-1] if '=' in version else version
    except (FileNotFoundError, IOError) as e:
        logging.exception(f'Unable to read properties file:\n{e}')
        return 'na'


app = web.Application()
app.add_routes(routes)
request_queue = asyncio.Queue()

log.info(f'Service version: {read_version_properties("version.properties")}')
logging.info(f'Configuration: {json.dumps(vars(cfg), indent=4)}')


if __name__ == '__main__':
    web.run_app(app, port=cfg.listening_port)
