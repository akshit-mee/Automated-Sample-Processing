from bot.bot import MattermostBot

def main():
    bot = MattermostBot()
    bot.start()
    
    # Keep the bot running
    import time
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()

