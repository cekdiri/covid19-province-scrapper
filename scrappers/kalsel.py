import datetime
import json

import dateparser
import requests
from bs4 import BeautifulSoup as soup
from peewee import fn

from models import Province, KabupatenKota, Data


def scrape():
    prov = __name__.split(".")[-1]
    propinsi = Province.select().where(Province.nama_prov == "Kalimantan Selatan")
    if propinsi.count() < 1:
        propinsi = Province.create(nama_prov="Kalimantan Selatan", alias=prov)
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

    link = "https://corona.kalselprov.go.id/cov_map"
    output = {}
    output["result"] = []
    with requests.session() as s:
        r = s.get(link, verify=True)
        data = r.text
        json_data = json.loads(data)
        # print(json_data)
        for data in json_data:
            list_item = {}
            list_item["provinsi"] = "Kalimantan Selatan"
            list_item["kode_kab_kota"] = data["code"]
            list_item["kab_kota"] = data["name"]
            list_item["kecamatan"] = "N/A"
            list_item["populasi"] = "N/A"
            list_item["lat_kab_kota"] = "N/A"
            list_item["long_kab_kota"] = "N/A"
            list_item["n_odr"] = "N/A"
            list_item["n_otg"] = "N/A"
            list_item["n_odp"] = data["cov_odp_count"]
            list_item["n_pdp"] = data["cov_pdp_count"]
            list_item["n_confirm"] = data["cov_positive_count"]
            list_item["n_meninggal"] = data["cov_died_count"]
            list_item["n_sembuh"] = data["cov_recovered_count"]
            list_item["last_update"] = "N/A"
            kabkota = KabupatenKota.select().where(
                KabupatenKota.prov_id == propinsi, KabupatenKota.nama == data["name"]
            )

            if kabkota.count() < 1:
                kabkota = KabupatenKota.create(
                    prov_id=propinsi, nama=data["name"], kode=data["code"]
                )
            else:
                kabkota = kabkota.get()
            datum = Data.select().where(
                Data.kabupaten == kabkota, Data.last_update == datetime.datetime.now()
            )
            if datum.count() < 1:
                datum = Data.create(
                    kabupaten=kabkota,
                    n_odp=data["cov_odp_count"],
                    n_pdp=data["cov_pdp_count"],
                    n_confirm=data["cov_positive_count"],
                    n_meninggal=data["cov_died_count"],
                    n_sembuh=data["cov_recovered_count"],
                    last_update=datetime.datetime.now(),
                )
            output["result"].append(list_item)

    return output

