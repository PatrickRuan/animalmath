from flask import Flask, request, jsonify 


app = Flask(__name__)

# Init session cache
session_next = {}
session_restaurant = {}

@app.route('/', methods=['POST'])
def webhook():
    """This method handles the http requests for the Dialogflow webhook
    This is meant to be used in conjunction with the weather Dialogflow agent
    """
    req = request.get_json(silent=True, force=True)
    if req['queryResult']['intent']['displayName'] == 'Greeting':
        
        if req['queryResult']['parameters']['animal'] == 'cat':
            return jsonify({"fulfillmentText":" 我們一起學貓鬼叫~ 喵喵喵!"})
        else :
            return jsonify({"fulfillmentText":" 哈囉 請問你想找哪隻動物 目前在線的可愛動物有 小豬 小狗 小貓"})
            
    if req['queryResult']['intent']['displayName'] == 'ask_math':
        
        if req['queryResult']['parameters']['operator'] == "+" :
            number = req['queryResult']['parameters']['number'] + req['queryResult']['parameters']['number1']
            
                
            #if req['queryResult']['parameters']['cat'] == 'cat':
            if number <= 20:
                ans = "喵!" * int(number)
                return jsonify({"fulfillmentText":"{}。喵了{}次，我要罐罐~".format(ans, int(number))})
            elif number >20:
                return jsonify({"fulfillmentText":"喵!喵!喵! 我要喵{}次，很累ㄟ。".format(int(number))})
            #else:
            #    return jsonify({"fulfillmentText":"你不找咪咪嗎"})
            
        
    else:
        return jsonify({"fulfillmentText":"你不找咪咪嗎?"})
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
