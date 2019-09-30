from .models import *

def use_messages(request):

    use_messages_str = str(LocalSettings.objects.first().use_messages)
    
    return {'use_messages_str': use_messages_str}