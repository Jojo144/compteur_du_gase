
def incr_key(dic, key, value):
    if key in dic:
        dic[key] += value
    else:
        dic[key] = value


def default_value(v, default):
    if v is None:
        return default
    else:
        return v

def round_stock(value):
    v = abs(value)
    if v >= 100:
        return '{0:.0f}'.format(value)
    if v >= 10:
        return '{0:.1f}'.format(value).rstrip('0').rstrip('.')
    if v >= 1:
        return '{0:.2f}'.format(value).rstrip('0').rstrip('.')
    if v == 0:
        return '0'
    else:
        return '{0:.3f}'.format(value)

def bool_to_utf8(b):
    if b:
        return "✔"
    else:
        return "✘"