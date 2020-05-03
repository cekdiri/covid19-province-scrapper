import datetime
import json
import re

import dateparser
import requests
from bs4 import BeautifulSoup as soup
from peewee import fn

from models import Province, KabupatenKota, Data


def scrape():
    prov = __name__.split(".")[-1]
    propinsi = Province.select().where(Province.nama_prov == "Jawa Timur")
    if propinsi.count() < 1:
        propinsi = Province.create(nama_prov="Jawa Timur", alias=prov)
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
    link = "http://covid19dev.jatimprov.go.id/xweb/draxi"
    output = {}
    output["result"] = []
    with requests.session() as s:
        r = s.get(link, verify=True)
        data = r.text
        url = soup(data, "lxml")

        script = url.find_all("script")
        json_data = ""
        for item in script:
            if re.search(r"datakabupaten=(\[{.*\}\])", str(item)):
                var_data = re.findall(r"datakabupaten=(\[{.*\}\])", str(item))
                json_data = json.loads(str(var_data[0]))

        for data in json_data:
            list_item = {}
            list_item["provinsi"] = "Jawa Timur"
            list_item["kode_kab_kota"] = data["kode"]
            list_item["kab_kota"] = data["kabko"]
            list_item["kecamatan"] = "N/A"
            list_item["populasi"] = "N/A"
            list_item["lat_kab_kota"] = data["lat"]
            list_item["long_kab_kota"] = data["lon"]
            list_item["n_odr"] = data["odr"]
            list_item["n_otg"] = data["otg"]
            list_item["n_odp"] = data["odp"]
            list_item["n_pdp"] = data["pdp"]
            list_item["n_confirm"] = data["confirm"]
            list_item["n_meninggal"] = data["meninggal"]
            list_item["n_sembuh"] = data["sembuh"]
            list_item["last_update"] = data["updated_at"]

            kabkota = KabupatenKota.select().where(
                KabupatenKota.prov_id == propinsi,
                KabupatenKota.nama == data["kabko"],
                KabupatenKota.kode == data["kode"],
            )

            if kabkota.count() < 1:
                kabkota = KabupatenKota.create(
                    prov_id=propinsi,
                    nama=data["kabko"],
                    kode=data["kode"],
                    lat=data["lat"],
                    lon=data["lon"],
                    populasi="",
                )
            else:
                kabkota = kabkota.get()

            datum = Data.select().where(
                Data.kabupaten == kabkota,
                Data.last_update == dateparser.parse(data["updated_at"]),
            )
            if datum.count() < 1:
                datum = Data.create(
                    kabupaten=kabkota,
                    n_odr=data["odr"],
                    n_otg=data["otg"],
                    n_odp=data["odp"],
                    n_pdp=data["pdp"],
                    n_confirm=data["confirm"],
                    n_meninggal=data["meninggal"],
                    n_sembuh=data["sembuh"],
                    last_update=dateparser.parse(data["updated_at"]),
                )

            output["result"].append(list_item)

    return output

