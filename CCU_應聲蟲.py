# 採用 reply token + 自編文字 ~~  (去擷取收到的訊息)

from flask import Flask, request, abort
import json

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

#token
line_bot_api = LineBotApi('xKHVznnDNhbuOnqk8MAc4gWIDZfGYQ2Hes71kBdnXKpNTKbX7vP1er/dw4PbaKG62XA07725iX4G2zRXQfQBVa+50XdYz0ejqD3/qW1WehWf1bERs0VSa6XBbwaLE8Re3C9NH+ScLNgTlIC6rpEaIQdB04t89/1O/w1cDnyilFU=')
#secret
handler = WebhookHandler('7e8743d954d434c0af89313fa978bf02')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    data = request.get_json()
    app.logger.info("Request body: " + body)
    text = data['events'][0]['message']['text']+' Patrick' # <== body is a string, so can't fetch structure data... 
    # handle webhook body
    try:
        #handler.handle(body, signature)
         line_bot_api.reply_message(data['events'][0]['replyToken'], TextSendMessage(text=text))
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    #app.run()
    app.run(host='0.0.0.0', port=8080, threaded=True)
    
    
