import datetime
import json

import dateparser
import requests
from bs4 import BeautifulSoup as soup
from peewee import fn

from models import Province, KabupatenKota, Data


def scrape():
    prov = __name__.split(".")[-1]
    propinsi = Province.select().where(Province.nama_prov == "Aceh")
    if propinsi.count() < 1:
        propinsi = Province.create(nama_prov="Aceh", alias=prov)
    else:
        propinsi = propinsi.get()
    sekarang = datetime.datetime.now().date()
    try:
        result = list(
            Data.select()
            .join(Province)
            .where(fn.date_trunc("day", Data.last_update) == sekarang),
            Province.alias == prov,
        )
    except:
        result = []
    if len(result) > 0:
        return result

    link = "https://covid.bravo.siat.web.id/json/peta"
    output = {}
    output["result"] = []
    with requests.session() as s:
        r = s.get(link, verify=True)
        data = r.text
        json_data = json.loads(data)
        # print(json_data)
        for data in json_data:
            list_item = {}
            list_item["provinsi"] = "Aceh"
            list_item["kode_kab_kota"] = "N/A"
            list_item["kab_kota"] = data["namaKabupaten"]
            list_item["kecamatan"] = "N/A"
            list_item["populasi"] = "N/A"
            list_item["lat_kab_kota"] = data["latitude"]
            list_item["long_kab_kota"] = data["longitude"]
            list_item["n_odr"] = "N/A"
            list_item["n_otg"] = "N/A"
            list_item["n_odp"] = data["odp"]
            list_item["n_pdp"] = data["pdp"]
            list_item["n_confirm"] = data["positif"]
            list_item["n_meninggal"] = data["positifMeninggal"]
            list_item["n_sembuh"] = data["positifSembuh"]
            list_item["last_update"] = data["updateDate"]

            kabkota = KabupatenKota.select().where(
                KabupatenKota.prov_id == propinsi,
                KabupatenKota.nama == data["namaKabupaten"],
            )

            if kabkota.count() < 1:
                kabkota = KabupatenKota.create(
                    prov_id=propinsi,
                    nama=data["namaKabupaten"],
                    lat=data["latitude"],
                    lon=data["longitude"],
                )
            else:
                kabkota = kabkota.get()
            datum = Data.select().where(
                Data.kabupaten == kabkota,
                Data.last_update == dateparser.parse(data["updateDate"]),
            )
            if datum.count() < 1:
                datum = Data.create(
                    kabupaten=kabkota,
                    n_odp=data["odp"],
                    n_pdp=data["pdp"],
                    n_confirm=data["positif"],
                    n_meninggal=data["positifMeninggal"],
                    n_sembuh=data["positifSembuh"],
                    last_update=dateparser.parse(data["updateDate"]),
                )
            output["result"].append(list_item)

    return output

