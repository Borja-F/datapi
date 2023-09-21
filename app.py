from flask_cors import CORS, cross_origin
from flask import request
from flask import json
from flask import Flask
import pymongo
from sentence_transformers import SentenceTransformer
from spanlp.palabrota import Palabrota
from scipy.spatial import distance
from flask import Flask, render_template, request, url_for, flash, redirect

app = Flask(__name__)
cors = CORS(app)
uri = "mongodb+srv://adrianpastorlopez09:nHSgK7jFZNLPANx6@cluster0.uw7fvq9.mongodb.net/"
myclient = pymongo.MongoClient(uri)
db = myclient["group2-back"]
questions = db["questions"]

model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')



@app.route('/')
def hello():
    return render_template('home.html')

@app.route('/api/v1/nlp/text/censor', methods = ['PUT'])
@cross_origin()
def censor():
    print("what")
    try:
        body = request.json
        in_message = body['message']
        print("what")
        
        if in_message and len(str(in_message).strip()):
            print("what")
            palabrota = Palabrota()
            response = palabrota.contains_palabrota(in_message)
            print("what")
            if response == True:
                msg = "Me estoy volviendo loco"

                return msg, {"censurado":True}
            else:
                msg = "Me estoy volviendo loco"

                return msg, {"censurado":False}
            print("what")

        else:
            print("what")
            return "what", {
                "success": False,
                "message": "Bad Request - message is required",
                "error_code": 400,
                "data": {}
            } 
        
    except Exception as e:
        return "what",{
            "success": False,
            "message": "Internal Server Error - "+str(e),
            "error_code": 500,
            "data": {}
        }


@app.route('/api/v1/nlp/text/seleccionador', methods = ['POST'])
@cross_origin()
def seleccionador():

        try:
            body = request.json
            in_message = body['message']
            embeddings1 = model.encode(in_message)
            where = {} 
            select = {"_id":False, "body":True} # cogemos solo el body

            preguntas = list(questions.find(where,select))
            l_preguntas = [question['body'] for question in preguntas]
            embeddings = model.encode(l_preguntas)
            repetido = {"repetido":False}
            for main in embeddings:

                similarity = (1 - distance.cosine(main, embeddings1))

                if similarity >= 0.68:
                        repetido = {"repetido":True}
                        break
            return repetido
                     
            

        except Exception as e:
            return {
                "success": False,
                "message": "Internal Server Error - "+str(e),
                "error_code": 500,
                "data": {}
            }


if __name__ == '__main__':
    app.run( debug=True)
# if __name__ == '__main__':
#     app.run(host='127.0.0.1', port=5000, debug=True)