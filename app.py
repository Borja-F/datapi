from flask_cors import CORS, cross_origin
from flask import request
from flask import json
from flask import Flask

from spanlp.palabrota import Palabrota

app = Flask(__name__)
cors = CORS(app)

@app.route('/api/v1/nlp/text/censor', methods = ['POST'])
@cross_origin()
def censor():
    try:
        body = request.json
        in_message = body['message']
        
        if in_message and len(str(in_message).strip()):
            palabrota = Palabrota()
            response = palabrota.contains_palabrota(in_message)
            if response == True:
                # message = "Lávate la boquita"
                return True
            else:
                # message = in_message
                return False
            # censored = palabrota.censor(in_message)
            # response = {
            #     "success": True,
            #     "message": "OK",
            #     "error_code": 0,
            #     "data": {
            #         'message': in_message,
            #         'censored': censored
            #     }
            # }
            # return response
        else:
            return {
                "success": False,
                "message": "Bad Request - message is required",
                "error_code": 400,
                "data": {}
            }
    except Exception as e:
        return {
            "success": False,
            "message": "Internal Server Error - "+str(e),
            "error_code": 500,
            "data": {}
        }


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)