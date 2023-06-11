import re

from cleantext import clean

words_to_delete = [
    'SL : PAID',
    'SL :  VIP GROUP',
    'Note :- Only for Education Purpose not any type of financial advice',
    'target : paid',
    'target :  VIP GROUP',
    'target:-your',
    'sl:-paid',
    '𝗧𝗔𝗥𝗚𝗘𝗧:-𝗬𝗼𝘂𝗿',
    '𝗦𝗟:-𝗣𝗮𝗶𝗱',
    'tgt open',
    'i am holding it till expiry',
    'hold',
    'till expiry',
]


def check_string_contains_all(input_string, substrings):
    for substring in substrings:
        pattern = re.compile(substring, re.IGNORECASE)
        if not re.search(pattern, input_string):
            return False
    return True


def delete_words(string, words):
    # Create a regular expression pattern to match the words to delete
    pattern = r'\b({})\b'.format('|'.join(re.escape(word) for word in words))
    # Use the pattern to find and remove the words from the text
    cleaned_string = re.sub(pattern, '', string, flags=re.IGNORECASE)
    return cleaned_string


def delete_emojis(string):
    return clean(string, no_emoji=True)


def remove_brackets(string):
    pattern = r'\[.*?\]|\(.*?\)'
    cleaned_string = re.sub(pattern, '', string)
    return cleaned_string


def remove_special_characters(string):
    # Define the pattern for special characters
    pattern = r'[^a-zA-Z0-9\s]'
    # Remove special characters using regular expression substitution
    cleaned_string = re.sub(pattern, ' ', string)
    return cleaned_string


def remove_extra_spaces(string):
    # lines = string.split("\n")
    # cleaned_lines = []
    # for line in lines:
    #     # Use regular expressions to replace multiple spaces with a single space
    #     cleaned_line = re.sub(r'\s+', ' ', line)
    #     cleaned_lines.append(cleaned_line)
    # cleaned_text = "\n".join(cleaned_lines)
    # Use regular expressions to replace multiple spaces with a single space
    cleaned_text = re.sub(r'[^\S\r\n]+', ' ', string)
    return cleaned_text.strip()


def format_message(message):
    formatted = delete_words(message, words_to_delete)
    formatted = delete_emojis(formatted)
    formatted = remove_brackets(formatted)
    formatted = remove_special_characters(formatted)
    formatted = remove_extra_spaces(formatted)
    return formatted.upper()


def remove_spaces(text):
    # Remove extra spaces and newlines
    cleaned_text = re.sub(r'\s+', ' ', text)
    return cleaned_text.strip()


def get_order_details(message, expiry):
    index = None
    instrument = None
    strike = None
    trigger = None
    target = None
    stoploss = None
    ce_or_pe = None

    msg_list = remove_spaces(message).split(' ')

    if 'BANKNIFTY' in msg_list:
        index = 'BANKNIFTY'
    elif 'NIFTY' in msg_list:
        index = 'NIFTY'

    if index:
        strike_idx = msg_list.index(index) + 1
        strike = msg_list[strike_idx]

        ce_or_pe_idx = msg_list.index(index) + 2
        ce_or_pe = msg_list[ce_or_pe_idx]

        if len(strike) == 5 and (ce_or_pe == 'CE' or ce_or_pe == 'PE'):
            instrument = f'OPTIDX_{index}_{expiry}_{ce_or_pe}_{strike}'
            trigger_idx = msg_list.index('ABOVE') + 1
            target_idx = msg_list.index('TARGET') + 1
            stoploss_idx = msg_list.index('SL') + 1
            if msg_list[trigger_idx].isnumeric() and msg_list[target_idx].isnumeric() and msg_list[stoploss_idx].isnumeric():
                trigger = int(msg_list[trigger_idx])
                target = int(msg_list[target_idx])
                stoploss = int(msg_list[stoploss_idx])

    return index, instrument, strike, trigger, target, stoploss, ce_or_pe
