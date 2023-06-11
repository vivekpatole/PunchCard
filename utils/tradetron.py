import logging
from datetime import datetime as dt

import requests

logger = logging.getLogger(__name__)


def get_params(set_no, instrument, strike, trigger, target, stoploss):
    lots = 2
    return f'&key=instrument{set_no}&value={instrument}' \
           f'&key1=strike{set_no}&value1={strike}' \
           f'&key2=trigger{set_no}&value2={trigger}' \
           f'&key3=target{set_no}&value3={target}' \
           f'&key4=stoploss{set_no}&value4={stoploss}' \
           f'&key5=lots{set_no}&value5={lots}' \
           f'&key6=exit{set_no}&value6=0' \
           f'&key7=start{set_no}&value7={set_no}' \
           f'&key8=trigger_time{set_no}&value8={dt.now().strftime("%H:%M:%S")}' \
           f'&key9=exit_all&value9=0'


def punch_order(tradetron, order):
    try:
        params = {}

        index, instrument, strike, trigger, target, stoploss, ce_or_pe = order['index'], order['instrument'], order[
            'strike'], order['trigger'], order['target'], order['stoploss'], order['ce_or_pe']

        if index == 'BANKNIFTY':
            if ce_or_pe == 'CE':
                params = get_params(set_no=1, instrument=instrument, strike=strike, trigger=trigger, target=target,
                                    stoploss=stoploss)
            elif ce_or_pe == 'PE':
                params = get_params(set_no=2, instrument=instrument, strike=strike, trigger=trigger, target=target,
                                    stoploss=stoploss)
        elif index == 'NIFTY':
            if ce_or_pe == 'CE':
                params = get_params(set_no=3, instrument=instrument, strike=strike, trigger=trigger, target=target,
                                    stoploss=stoploss)
            elif ce_or_pe == 'PE':
                params = get_params(set_no=4, instrument=instrument, strike=strike, trigger=trigger, target=target,
                                    stoploss=stoploss)

        logger.info(f'Query Params: {params}')

        url, auth_token_live, auth_token_paper = tradetron['url'], tradetron['auth_token']['live'], \
            tradetron['auth_token']['paper']

        # Paper Trade
        paper_url = f'{url}auth-token={auth_token_paper}{params}'
        logger.info(f'Paper Request: {paper_url}')
        response = requests.get(url=paper_url)
        log_message = f'Paper TT Response: {response.text}'
        logger.info(log_message)

        # Live Trade https://api.tradetron.tech/api?auth-token=73521081-efa2-4b9b-bda9-87a2ccc4ea83
        # live_url = f'{url}auth-token={auth_token_live}{params}'
        # logger.info(f'Live Request: {live_url}')
        # response = requests.get(url=live_url)
        # log_message = f'Live TT Response: {response.text}'
        # logger.info(log_message)

    except Exception as e:
        log_message = f'Error occurred while placing order: {e}'
        logger.error(log_message)
