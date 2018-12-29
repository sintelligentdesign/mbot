from mastodon import Mastodon
from mastodon import StreamListener

# Create Mastodon API instance
mastodon = Mastodon(
    access_token = 'emma_usercred.secret',
    api_base_url = 'https://botsin.space'
)

class stdOutListener(StreamListener):
    def on_update(self, status):
        # print status
        return True

    def on_notification(self, status):
        if status.type == 'mention':
            print status
            return True
        else:
            return False

# Stream events
print mastodon.stream_user(
    listener=stdOutListener()
)