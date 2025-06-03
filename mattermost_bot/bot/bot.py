from mattermostdriver import Driver
from config.settings import Config

class MattermostBot:
    def __init__(self):
        Config.validate()
        
        self.driver = Driver({
            'url': Config.MATTERMOST_URL,
            'port': Config.MATTERMOST_PORT,
            'token': Config.BOT_TOKEN,
            'scheme': 'https',
            'basepath': '/api/v4',
            'verify': True,
            'timeout': 30,
        })
        
        self.team_id = None
        self.user_id = None
        
    def connect(self):
        """Connect to Mattermost server"""
        self.driver.login()
        self.user_id = self.driver.users.get_user_by_username(
            Config.BOT_USERNAME)['id']
        self.team_id = self.driver.teams.get_team_by_name(
            Config.BOT_TEAM)['id']
        
    def start(self):
        """Start listening for messages"""
        self.connect()
        print(f"Bot {Config.BOT_USERNAME} connected to {Config.MATTERMOST_URL}")
        
        @self.driver.on('posted')
        def posted(post):
            self.handle_post(post)
            
    def handle_post(self, post):
        """Handle incoming posts"""
        data = post['data']
        channel_id = data['channel_id']
        message = data['message']
        
        # Skip our own messages and system messages
        if 'sender_name' not in data or data['sender_name'] == Config.BOT_USERNAME:
            return
            
        print(f"Received message in channel {channel_id}: {message}")
        
        # Add your message handling logic here
        if 'hello' in message.lower():
            self.post_message(channel_id, f"Hello there, {data['sender_name']}!")
            
    def post_message(self, channel_id, message):
        """Post a message to a channel"""
        self.driver.posts.create_post({
            'channel_id': channel_id,
            'message': message
        })
