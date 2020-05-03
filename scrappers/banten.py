import datetime
import json
import re

import dateparser
import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
from peewee import fn

from models import Province, KabupatenKota, Data


def scrape():
    prov = __name__.split(".")[-1]
    propinsi = Province.select().where(Province.nama_prov == "Banten")
    if propinsi.count() < 1:
        propinsi = Province.create(nama_prov="Banten", alias=prov)
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
    link = "https://infocorona.bantenprov.go.id/"
    output = {}
    output["result"] = []
    with requests.session() as s:
        r = s.get(link, verify=True)
        data = r.text
        url = soup(data, "lxml")

        script = url.find_all("script")
        json_data = ""
        for item in script:
            if re.search(r"pieSeries.data\s\=\s(.*)\;", str(item)):
                var_data = re.findall(r"pieSeries.data\s\=\s(.*)\;", str(item))
                json_data = json.loads(str(var_data[0]))

        for data in json_data:
            list_item = {}
            list_item["provinsi"] = "Banten"
            list_item["kode_kab_kota"] = "N/A"
            list_item["kab_kota"] = data["title"]
            list_item["kecamatan"] = "N/A"
            list_item["populasi"] = "N/A"
            list_item["lat_kab_kota"] = data["latitude"]
            list_item["long_kab_kota"] = data["longitude"]
            list_item["n_odr"] = "N/A"
            list_item["n_otg"] = "N/A"
            list_item["n_odp"] = data["pieData"][0]["value"]
            list_item["n_pdp"] = data["pieData"][1]["value"]
            list_item["n_confirm"] = data["pieData"][2]["value"]
            list_item["n_meninggal"] = "N/A"
            list_item["n_sembuh"] = "N/A"
            list_item["last_update"] = "N/A"

            kabkota = KabupatenKota.select().where(
                KabupatenKota.prov_id == propinsi, KabupatenKota.nama == data["title"]
            )

            if kabkota.count() < 1:
                kabkota = KabupatenKota.create(
                    prov_id=propinsi,
                    nama=data["title"],
                    lat=data["latitude"],
                    lon=data["longitude"],
                    populasi="",
                )
            else:
                kabkota = kabkota.get()

            datum = Data.select().where(
                Data.kabupaten == kabkota, Data.last_update == datetime.datetime.now()
            )
            if datum.count() < 1:
                datum = Data.create(
                    kabupaten=kabkota,
                    n_odp=data["pieData"][0]["value"],
                    n_pdp=data["pieData"][1]["value"],
                    n_confirm=data["pieData"][2]["value"],
                    last_update=datetime.datetime.now(),
                )

            output["result"].append(list_item)

    return output

