from flask_cors import CORS, cross_origin
from flask import request
from flask import json
from flask import Flask
import pymongo
# from sentence_transformers import SentenceTransformer
from spanlp.palabrota import Palabrota
from scipy.spatial import distance
from flask import Flask, render_template, request, url_for, flash, redirect
from flask import Flask, request, render_template, jsonify
import numpy as np
# import replicate
import os
import pandas as pd
import numpy as np

import psycopg2
from sqlalchemy import create_engine
from datetime import datetime




app = Flask(__name__)
cors = CORS(app)
uri = "mongodb+srv://adrianpastorlopez09:nHSgK7jFZNLPANx6@cluster0.uw7fvq9.mongodb.net/"
myclient = pymongo.MongoClient(uri)
db = myclient["group2-back"]
questions = db["questions"]
os.environ['REPLICATE_API_TOKEN'] = "r8_3Cn377wOsZ8ywqtFyCCicG5JwHqpHYS0sONIW"
engine = create_engine('postgresql://fl0user:ClU4ueygKz9G@ep-red-butterfly-89282058.eu-central-1.aws.neon.tech:5432/spaces?sslmode=require')
# model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')



@app.route('/')
def hello():
    return render_template('home.html')

@app.route('/api/v1/nlp/text/censor', methods = ['POST'])
@cross_origin()
def censor():
   
    try:
        body = request.json
        in_message = body['message']
       
        
        if in_message and len(str(in_message).strip()):
           
            palabrota = Palabrota()
            response = palabrota.contains_palabrota(in_message)
            print("what")
            if response == True:
                

                return {"censurado":True}
            else:
                msg = "Me estoy volviendo loco"

                return {"censurado":False}
           

        else:
           
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
    





@app.route("/img_det", methods=["GET", "POST"])
@cross_origin()
def img_nsfw():
    import requests
    if request.method == "POST":
        # Obtener el archivo de imagen desde el formulario
        img = request.files['image']
        print(img)
        # Verificar si se seleccionó un archivo
        if img:
            # Crear una solicitud POST con el archivo de imagen
            url = "https://nsfw-images-detection-and-classification.p.rapidapi.com/adult-content-file"

            # El encabezado Content-Type se configurará automáticamente con 'multipart/form-data'

            # Crea un diccionario para contener los datos del formulario y la imagen
            data = {}
            data['image'] = (img.filename, img, img.content_type)

            # Agrega los encabezados necesarios
            headers = {
                "X-RapidAPI-Key": "c679110cc2msh7f219734fbb8848p15052ejsnd747bb937243",
                "X-RapidAPI-Host": "nsfw-images-detection-and-classification.p.rapidapi.com"
            }

            # Realiza la solicitud POST con los datos y encabezados
            response = requests.post(url, files=data, headers=headers)
            
            # Meter todo en base d datos:

            cols = {
                'user':'-',
                'img': data,
                'response':str(response.json()['objects']),
                'unsafe':str(response.json()['unsafe'])
            }
            index = [int(datetime.now().timestamp())]
            df = pd.DataFrame(cols, index= index)
            df.to_sql(name="pic_control",if_exists='append',con=engine, index = False)
            
            
            return jsonify(response.json())
        return render_template('img_form.html')

    return render_template('img_form.html')



# @app.route('/api/v1/nlp/text/seleccionador', methods = ['POST'])
# @cross_origin()
# def seleccionador():

#         try:
#             body = request.json
#             in_message = body['message']
#             embeddings1 = model.encode(in_message)
#             where = {} 
#             select = {"_id":False, "body":True} # cogemos solo el body

#             preguntas = list(questions.find(where,select))
#             l_preguntas = [question['body'] for question in preguntas]
#             embeddings = model.encode(l_preguntas)
#             repetido = {"repetido":False}
#             for main in embeddings:

#                 similarity = (1 - distance.cosine(main, embeddings1))

#                 if similarity >= 0.68:
#                         repetido = {"repetido":True}
#                         break
#             return repetido
                     
            

#         except Exception as e:
#             return {
#                 "success": False,
#                 "message": "Internal Server Error - "+str(e),
#                 "error_code": 500,
#                 "data": {}
#             }


# if __name__ == '__main__':
#     app.run( debug=True)
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)