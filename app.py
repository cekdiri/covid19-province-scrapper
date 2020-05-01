from flask import Flask,jsonify,request
from flasgger import Swagger
import json

from Scrapper import Scrapper as scr

coronaID = Flask(__name__)
Swagger(coronaID)

@coronaID.route('/api/prov/<string:prov>', methods=['GET'])
def api(prov):
    """
    Endpoint untuk mendapatkan data kasus Covid19 di beberapa provinsi yang ada di Indonesia
    ---
    tags:
        - Rest Controller
    parameters:
        - name: body
          in: body
          required: true
          schema:
            id: Provinsi
            required:
                - provinsi
            properties:
                provinsi:
                    type: string
                    description: Silahkan isikan akronim nama provinsi yang akan Anda ambil data kasus Covid19 yang terjadi di provinsi terebut. Saat ini baru tersedia untuk aceh, bali, diy, sumut, babel, jatim, kalsel, dan sulses
                    default: ""
    responses:
        200:
            description: Berhasil
        400:
            description: Mohon maaf, ada permasalahan dalam memproses permintaan Anda
    """
    
    #post = request.get_json()
    #prov = post['provinsi']
  
    return jsonify(scr.scrapper(prov))

#coronaID.run(debug=True)
if __name__ == '__main__':
   coronaID.run(debug=False)