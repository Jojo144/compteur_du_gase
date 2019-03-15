
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
