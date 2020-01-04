from .models import *

def base_processor(request):
    return {'use_messages': get_local_settings().use_messages,
            }
