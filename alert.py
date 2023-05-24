import requests
import json
import pymsteams
from inputs import TELEGRAM_TOKEN



def send_telegram(msg, chatid):
    if chatid != 'none' and chatid:
        BOT_SEND_MSG_URL = 'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&parse_mode=HTML&disable_notification=None&text={msg}'
        url = BOT_SEND_MSG_URL.format(token=TELEGRAM_TOKEN, chat_id=chatid, msg=msg)
        try:
            r = requests.get(url)
            result = json.loads(r.text)
            print (result)
            return result.get('ok', False)
        except Exception as e:
            print (e)

def send_teams(msg, botid):
    if botid != 'none' and botid:
        myTeamsMessage = pymsteams.connectorcard(str(botid))
        myTeamsMessage.text(msg)
        myTeamsMessage.send()
