import logging
from datetime import datetime as dt

import yaml
from telethon import TelegramClient, events, sync

from utils.message_scraper import format_message, check_string_contains_all, delete_emojis, remove_spaces, \
    get_order_details
from utils.notification import send_telegram_message
from utils.nse import get_expiry
from utils.tradetron import punch_order

log_file = f'logs/PC{dt.now().strftime("%Y%m%d")}.log'
log_format = '%(asctime)s [%(levelname)s] - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

channel_ids = []
telegram = {}
trade_setup = {}
tradetron = {}


def read_config():
    logger.info('Reading config file...')

    with open('config/config.yaml') as file:
        try:
            db_config = yaml.safe_load(file)

            telegram['api_id'] = db_config['telegram']['api_id']
            telegram['api_hash'] = db_config['telegram']['api_hash']
            telegram['api_token'] = db_config['telegram']['api_token']
            telegram['username'] = db_config['telegram']['username']
            telegram['to_channels'] = {
                'the_tech_trader': db_config['message']['to_channels']['the_tech_trader'],
                'punch_card': db_config['message']['to_channels']['punch_card']
            }
            telegram['from_channels'] = db_config['message']['from_channels']
            telegram['filters'] = db_config['message']['filters']

            trade_setup['lot'] = db_config['trade_setup']['lot']
            trade_setup['exchange'] = db_config['trade_setup']['exchange'].upper()
            trade_setup['symbol'] = db_config['trade_setup']['symbol']

            tradetron['url'] = db_config['tradetron']['url']
            tradetron['auth_token'] = {
                'live': db_config['tradetron']['auth_token']['live'],
                'paper': db_config['tradetron']['auth_token']['paper']
            }

        except yaml.YAMLError as exc:
            log_message = f'{str(exc)}: Exception occur in read_config()'
            logger.info(log_message)


# Read configurations
read_config()
# Get current week expiry date from NSE
current_expiry = get_expiry('NIFTY')
# Create the client and connect
client = TelegramClient(telegram['username'], telegram['api_id'], telegram['api_hash'])


@client.on(events.NewMessage(chats=channel_ids))
async def message_listener(event):
    try:
        message = delete_emojis(event.message.message)
        if check_string_contains_all(message, telegram['filters']):
            # channel_id = event.message.peer_id.channel_id
            message = format_message(message)
            logger.info(f'Message: {remove_spaces(message)}')
            send_telegram_message(api_token=telegram['api_token'], chat_id=telegram['to_channels']['punch_card'],
                                  message=message)

            index, instrument, strike, trigger, target, stoploss, ce_or_pe = get_order_details(message=message,
                                                                                               expiry=current_expiry)
            log_message = f'Order Details: {index}, {instrument}, {strike}, {trigger}, {target}, {stoploss}, {ce_or_pe}'
            logger.info(log_message)

            if index and instrument and strike and trigger and target and stoploss and ce_or_pe:
                order = {
                    'index': index,
                    'instrument': instrument,
                    'strike': strike,
                    'trigger': trigger,
                    'target': target,
                    'stoploss': stoploss,
                    'ce_or_pe': ce_or_pe
                }
                punch_order(tradetron=tradetron, order=order)

                tele_message = f'ORDER TRIGGERED [{dt.now().strftime("%H:%M:%S")}]: {instrument}, {strike}, ' \
                               f'{trigger}, {target}, {stoploss}'
                logger.info(tele_message)
                send_telegram_message(api_token=telegram['api_token'],
                                      chat_id=telegram['to_channels']['the_tech_trader'], message=tele_message)

    except Exception as e:
        log_message = f'Error occurred in message_listener: {e}'
        logger.error(log_message)


if __name__ == '__main__':
    logger.info('Client started...')
    logger.info(f'Current Expiry: {current_expiry}')

    with client:
        # Get channel ids from channel list
        for channel in telegram['from_channels']:
            channel_entity = client.get_entity(channel)
            channel_ids.append(channel_entity.id)

        logger.info(f'Channel ID: {channel_ids}')

        # Runs the event loop until it is disconnected.
        client.run_until_disconnected()
