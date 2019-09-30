from .models import *

def use_messages(request):

    use_messages_str = str(LocalSettings.objects.first().use_messages)

    use_favicon_str = str(LocalSettings.objects.first().use_favicon)

    return {'use_messages_str': use_messages_str, 'use_favicon_str': use_favicon_str}
