import asyncio
from xml.etree import ElementTree
from datetime import datetime
from main import log
from config import cfg


class CorrectDate:
    today = datetime.strptime(datetime.strftime(datetime.today(), cfg.date_format), cfg.date_format)

    def __init__(self, processing_queue: asyncio.Queue):
        '''
        The CorrectDate class will take an asyncio queue as a parameter. The modify_xml() method
        will take an incoming request, parse the xml payload, compare the Date value to the current
        date and build a new payload with the correct date if it does not match. It will then
        append the new payload to the processing queue.

        :param processing_queue: asyncio.Queue: the current processing queue.
        '''

        self.processing_queue = processing_queue

    async def modify_xml(self, query_string):
        try:
            log.info('Parsing query string.')

            xml_data = ElementTree.fromstring(query_string['XMLData'])
            date = xml_data.find('Date')

            date.text = await self.get_correct_date(date.text)
            xml_str = ElementTree.tostring(xml_data, encoding='unicode', method='xml')

            # return xml_str
            await self.processing_queue.put(xml_str)

        except ElementTree.ParseError as e:
            log.error(f'Failed to parse xml payload: {e}')

    async def get_correct_date(self, date_text):
        log.info(f'Verifying date value: Payload date: {date_text} | Current date: {str(self.today).split(" ")[0]}')

        try:
            # Convert date string to datetime object
            dt_object = datetime.strptime(date_text, cfg.date_format)

            # Compare payload date to current date
            if dt_object != self.today:
                log.info('Updating payload to reflect current date.')
                current_date = datetime.strftime(self.today, cfg.date_format)
            else:
                log.info('Dates match. Nothing to do ¯\\_(ツ)_/¯')
                current_date = date_text

            return current_date

        except (ValueError, NameError) as e:
            log.error(f'Conversion/Comparison failed: {e}')
