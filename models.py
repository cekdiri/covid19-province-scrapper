import peewee as pw
from datetime import datetime, timedelta
from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')

db = pw.MySQLDatabase(app.config['NAME_DB'], user=app.config['USER_DB'], password=app.config['PASS_DB'],
                         host='127.0.0.1', port=3306)

class BaseModel(pw.Model):
    class Meta:
        database = db

class Province(BaseModel):
    nama_prov = pw.CharField(max_length=255)
    alias = pw.CharField(max_length=255)

class KabupatenKota(BaseModel):
    prov_id = pw.ForeignKeyField(Province, backref='provinsi')
    kode = pw.CharField(max_length=255, null=True)
    nama = pw.CharField(max_length=255, null=True)
    populasi = pw.CharField(max_length=255, null=True)
    lat = pw.CharField(max_length=255, null=True)
    lon = pw.CharField(max_length=255, null=True)

class Data(BaseModel):
    kabupaten = pw.ForeignKeyField(KabupatenKota, backref='kabupaten')
    n_odr     = pw.IntegerField(null=True)
    n_otg     = pw.IntegerField(null=True)
    n_odp     = pw.IntegerField(null=True)
    n_pdp     = pw.IntegerField(null=True)
    n_confirm = pw.IntegerField(null=True)
    n_meninggal = pw.IntegerField(null=True)
    n_sembuh = pw.IntegerField(null=True)
    last_update = pw.DateTimeField()
    created_at = pw.DateTimeField(default=datetime.utcnow())


db.connect()
db.create_tables([Province, KabupatenKota, Data], safe=True)