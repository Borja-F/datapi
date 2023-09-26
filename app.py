from flask_cors import CORS, cross_origin
from flask import Flask, request, json, send_file, render_template, url_for, flash, redirect, jsonify
import pymongo
from spanlp.palabrota import Palabrota
import os
import pandas as pd
import numpy as np
from docx import Document
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime
import secrets
import string
import qrcode
import base64
import io
from config import Config
from flask_sqlalchemy import SQLAlchemy
import requests





app = Flask(__name__)
app.config.from_object(Config) 
db_api = SQLAlchemy(app)
cors = CORS(app)
# uri = os.getenv("uri")
uri = "mongodb+srv://adrianpastorlopez09:nHSgK7jFZNLPANx6@cluster0.uw7fvq9.mongodb.net/"
myclient = pymongo.MongoClient(uri)
db = myclient["group2-back"]
questions = db["questions"]
os.environ['REPLICATE_API_TOKEN'] = "r8_3Cn377wOsZ8ywqtFyCCicG5JwHqpHYS0sONIW"
# engine = create_engine("apibase")
engine = create_engine('postgresql://fl0user:ClU4ueygKz9G@ep-red-butterfly-89282058.eu-central-1.aws.neon.tech:5432/spaces?sslmode=require')




@app.route('/')
def hello():
    return render_template('endpoints.html')

@app.route('/api/text/censor', methods = ['POST'])
@cross_origin()
def censor():
    from models import APIKey
    try:
        api_key = request.headers.get('API-Key')

        if not api_key:
            return jsonify({
                "success": False,
                "message": "Unauthorized - API key is missing",
                "error_code": 401,
                "data": {}
            }), 401

        # Check if the API key exists in the database
        api_key_record = db_api.session.query(APIKey).filter_by(key=api_key).first()
        if not api_key_record:
            return jsonify({
                "success": False,
                "message": "Unauthorized - Invalid API key",
                "error_code": 401,
                "data": {}
            }), 401

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
                    
                    return {"censurado":False}
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

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal Server Error - " + str(e),
            "error_code": 500,
            "data": {}
        }), 500







@app.route("/img_det", methods=["GET", "POST"])
@cross_origin()
def img_nsfw():
    from models import APIKey
    try:
        api_key = request.headers.get('API-Key')

        if not api_key:
            return jsonify({
                "success": False,
                "message": "Unauthorized - API key is missing",
                "error_code": 401,
                "data": {}
            }), 401

        # Check if the API key exists in the database
        api_key_record = db_api.session.query(APIKey).filter_by(key=api_key).first()
        if not api_key_record:
            return jsonify({
                "success": False,
                "message": "Unauthorized - Invalid API key",
                "error_code": 401,
                "data": {}
            }), 401
    
        if request.method == "POST":
            # Obtener el archivo de imagen desde el formulario
            img = request.files['image']
            user = request.headers["authorization"]
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
                json_response = response.json()
                unsafe_value = {"unsafe":json_response['unsafe']}
                
                # Meter todo en base de datos:

                cols = {
                    'user':user,
                    'img': data,
                    'response':str(response.json()['objects']),
                    'unsafe':str(response.json()['unsafe'])
                }
                index = [int(datetime.now().timestamp())]
                df = pd.DataFrame(cols, index= index)
                df.to_sql(name="pic_control",if_exists='append',con=engine, index = False)
                
                
                return unsafe_value
            return render_template('img_form.html')

        return render_template('img_form.html')
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal Server Error - " + str(e),
            "error_code": 500,
            "data": {}
        }), 500


@app.route("/volcar_coleccion", methods = ["POST"])
def volcador():
    from models import APIKey
    try:
        api_key = request.headers.get('API-Key')

        if not api_key:
            return jsonify({
                "success": False,
                "message": "Unauthorized - API key is missing",
                "error_code": 401,
                "data": {}
            }), 401

        # Check if the API key exists in the database
        api_key_record = db_api.session.query(APIKey).filter_by(key=api_key).first()
        if not api_key_record:
            return jsonify({
                "success": False,
                "message": "Unauthorized - Invalid API key",
                "error_code": 401,
                "data": {}
            }), 401
        source_collection = db['questions']
        target_collection = db['longterm']

        # get all documents from the source collection
        documents = list(source_collection.find({}))

        # insert the documents into the target collection
        target_collection.insert_many(documents)

        return "Colección volcada con éxito", 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal Server Error - " + str(e),
            "error_code": 500,
            "data": {}
        }), 500


@app.route("/descargar_preguntas", methods = ["POST"])
def descargador():
    from models import APIKey

    try:
        api_key = request.headers.get('API-Key')

        if not api_key:
            return jsonify({
                "success": False,
                "message": "Unauthorized - API key is missing",
                "error_code": 401,
                "data": {}
            }), 401

        # Check if the API key exists in the database
        api_key_record = db_api.session.query(APIKey).filter_by(key=api_key).first()
        if not api_key_record:
            return jsonify({
                "success": False,
                "message": "Unauthorized - Invalid API key",
                "error_code": 401,
                "data": {}
            }), 401

        where = {} 
        select = {"_id":False, "body":True}
        preguntas = list(questions.find(where,select))
        l_preguntas = [question['body'] for question in preguntas]

        # create a new Word document
        doc = Document()

        # add each item in the list to the document
        for item in l_preguntas:
            doc.add_paragraph(item)

        # save the document
        file_path = 'Preguntas.docx'
        doc.save(file_path)

        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal Server Error - " + str(e),
            "error_code": 500,
            "data": {}
        }), 500




@app.route("/vaciar_coleccion", methods = ["POST"])
def vaciador():
    from models import APIKey


    try:
        api_key = request.headers.get('API-Key')

        if not api_key:
            return jsonify({
                "success": False,
                "message": "Unauthorized - API key is missing",
                "error_code": 401,
                "data": {}
            }), 401

        # Check if the API key exists in the database
        api_key_record = db_api.session.query(APIKey).filter_by(key=api_key).first()
        if not api_key_record:
            return jsonify({
                "success": False,
                "message": "Unauthorized - Invalid API key",
                "error_code": 401,
                "data": {}
            }), 401
        

        collection = db['questions']


        collection.delete_many({})
        return "Colección vaciada con éxito", 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal Server Error - " + str(e),
            "error_code": 500,
            "data": {}
        }), 500



@app.route('/api/v1/admin/generate_api_key', methods=['POST'])
def generate_api_key():
    from models import APIKey

    try:
        api_key = request.headers.get('API-Key')

        if not api_key:
            return jsonify({
                "success": False,
                "message": "Unauthorized - API key is missing",
                "error_code": 401,
                "data": {}
            }), 401

        # Check if the API key exists in the database
        api_key_record = db_api.session.query(APIKey).filter_by(key=api_key).first()
        if not api_key_record:
            return jsonify({
                "success": False,
                "message": "Unauthorized - Invalid API key",
                "error_code": 401,
                "data": {}
            }), 401

        
        from models import APIKey
        api_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(Config.API_KEY_LENGTH))
        db_api.session.add(APIKey(key=api_key))
        db_api.session.commit()
        return api_key
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal Server Error - " + str(e),
            "error_code": 500,
            "data": {}
        }), 500


@app.route('/generate_qr_usuario', methods=['GET'])
def generate_qr_ususario():
    from models import APIKey

    try:
        api_key = request.headers.get('API-Key')

        if not api_key:
            return jsonify({
                "success": False,
                "message": "Unauthorized - API key is missing",
                "error_code": 401,
                "data": {}
            }), 401

        # Check if the API key exists in the database
        api_key_record = db_api.session.query(APIKey).filter_by(key=api_key).first()
        if not api_key_record:
            return jsonify({
                "success": False,
                "message": "Unauthorized - Invalid API key",
                "error_code": 401,
                "data": {}
            }), 401

        #Aquí, estás obteniendo los datos JSON que se envían con la solicitud. Estos datos se almacenan en la variable data
        data = request.get_json()
        #Aquí, estás extrayendo el valor de ‘id_usuario’ de los datos JSON y almacenándolo en la variable id_usuario.
        id_usuario = data['id_usuario']

        #Se crea un objeto QRCode y añades los datos del id_usuario al código QR.
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(id_usuario)
        qr.make(fit=True)

        #Aquí, estás generando una imagen del código QR con el color de fondo blanco y los cuadrados del código QR en negro.
        img = qr.make_image(fill='black', back_color='white')
        #Estás creando un objeto BytesIO para almacenar temporalmente la imagen del código QR.
        buffered = io.BytesIO()
        #Aquí, estás guardando la imagen del código QR en el objeto BytesIO en formato JPEG.
        img.save(buffered)

        #Estás codificando la imagen del código QR en base64 para poder enviarla como una cadena de texto.
        img_str = base64.b64encode(buffered.getvalue())
        #estás devolviendo un objeto JSON con la imagen del código QR codificada en base64 y un código de estado HTTP 200 para indicar que la solicitud se ha procesado con éxito.
        return jsonify({'qr_code': img_str.decode('utf-8')}), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal Server Error - " + str(e),
            "error_code": 500,
            "data": {}
        }), 500



@app.route('/generate_qr_usuario_evento', methods=['GET'])
def generate_qr_ususario_evento():
    from models import APIKey
        

    try:
        api_key = request.headers.get('API-Key')

        if not api_key:
            return jsonify({
                "success": False,
                "message": "Unauthorized - API key is missing",
                "error_code": 401,
                "data": {}
            }), 401

        # Check if the API key exists in the database
        api_key_record = db_api.session.query(APIKey).filter_by(key=api_key).first()
        if not api_key_record:
            return jsonify({
                "success": False,
                "message": "Unauthorized - Invalid API key",
                "error_code": 401,
                "data": {}
            }), 401

        data = request.get_json()
        id_usuario = data['id_usuario']
        id_evento = data['id_evento']

        qr_data = f"Usuario: {id_usuario}, Evento: {id_evento}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        buffered = io.BytesIO()
        img.save(buffered)

        img_str = base64.b64encode(buffered.getvalue())
        return jsonify({'qr_code': img_str.decode('utf-8')}), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal Server Error - " + str(e),
            "error_code": 500,
            "data": {}
        }), 500



# if __name__ == '__main__':
#     app.run( debug=True)
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)