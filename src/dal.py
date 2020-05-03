

def get_instrument_filter(code):
    if ':' in code:
        exchange_code, symbol = code.split(':')
    else:
        exchange_code = None
        symbol = code

    return {
        'exchange.code': exchange_code,
        'symbol': symbol
    }
