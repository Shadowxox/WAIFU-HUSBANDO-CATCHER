class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "7795212861"
    sudo_users = "7795212861", "5758240622", "7361967332"
    GROUP_ID = -1002680733244

    TOKEN = "7525650740:AAHujfrXw8A4F3YthCemnWm5re28AbPcYBY"
    mongo_url = "mongodb+srv://naruto:hinatababy@cluster0.rqyiyzx.mongodb.net/"
    PARTNER = "7361967332", "5758240622", "7795212861"
    PHOTO_URL = ["https://files.catbox.moe/h0qot3.jpg", "https://files.catbox.moe/tx0o73.jpg", "https://files.catbox.moe/rqwt42.jpg"]
    SUPPORT_CHAT = "-1002680733244"
    UPDATE_CHAT = "-1002621413939"
    BOT_USERNAME = "@Shadow_testingbot"
    CHARA_CHANNEL_ID = "-1002474756169"
    api_id = 23287799
    api_hash = "9f4f17dae2181ee22c275b9b40a3c907"


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
