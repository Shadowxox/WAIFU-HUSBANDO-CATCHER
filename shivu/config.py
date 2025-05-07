class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "7795212861"
    sudo_users = "7361967332", "5758240622", "7795212861"
    GROUP_ID = -1002643948280
    TOKEN = "7525650740:AAHujfrXw8A4F3YthCemnWm5re28AbPcYBY"
    mongo_url = "mongodb+srv://HaremDBBot:ThisIsPasswordForHaremDB@haremdb.swzjngj.mongodb.net/?retryWrites=true&w=majority"
    PHOTO_URL = ["https://i.ibb.co/RGm4r4q0/image.jpg", "https://i.ibb.co/Kcxbdcm4/image.jpg"]
    SUPPORT_CHAT = "hwkwjieie"
    UPDATE_CHAT = "hwkwjieie"
    BOT_USERNAME = "Shadow_testingbot"
    CHARA_CHANNEL_ID = "-1002133191051"
    api_id = 23287799
    api_hash = "9f4f17dae2181ee22c275b9b40a3c907"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
