class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "7795212861"
    sudo_users = "6845325416", "6765826972"
    GROUP_ID = -1002133191051
    TOKEN = "7369319572:AAEP7YLvQP3FQDwY2jMNpos-Zv9B4bnkctE"
    mongo_url = "mongodb+srv://HaremDBBot:ThisIsPasswordForHaremDB@haremdb.swzjngj.mongodb.net/?retryWrites=true&w=majority"
    PHOTO_URL = ["https://telegra.ph/file/b925c3985f0f325e62e17.jpg", "https://telegra.ph/file/4211fb191383d895dab9d.jpg"]
    SUPPORT_CHAT = "Collect_em_support"
    UPDATE_CHAT = "Collect_em_support"
    BOT_USERNAME = "Collect_Em_AllBot"
    CHARA_CHANNEL_ID = "-1002133191051"
    api_id = 23287799
    api_hash = "9f4f17dae2181ee22c275b9b40a3c907"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
