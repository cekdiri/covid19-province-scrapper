import datetime
import re

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
    link = "http://covid19.sumutprov.go.id/home"
    output = {}
    output["result"] = []
    with requests.session() as s:
        r = s.get(link, verify=True)
        data = r.text
        data = re.sub(r"<!--", "", data)
        data = re.sub(r"-->", "", data)
        url = soup(data, "lxml")

        table = url.find(
            "table",
            attrs={"class": "table table-striped table-bordered table-responsive"},
        )

        if table is not None:
            res = []
            table_rows = table.find_all("tr")

            num_rows = len(table_rows)
            # print(num_rows)

            i = 0
            for tr in table_rows:
                td = tr.find_all("td")
                row = [tr.text.strip() for tr in td if tr.text.strip()]
                # print(row)

                if i >= 1 and i < num_rows - 1:

                    list_item = {}
                    list_item["provinsi"] = "Sumatera Utara"
                    list_item["kode_kab_kota"] = "N/A"
                    list_item["kab_kota"] = str(row[1]).rstrip()

                    list_item["kecamatan"] = "N/A"
                    list_item["populasi"] = "N/A"
                    list_item["lat_kab_kota"] = "N/A"
                    list_item["long_kab_kota"] = "N/A"
                    list_item["n_odr"] = "N/A"
                    list_item["n_otg"] = "N/A"
                    list_item["n_odp"] = int(str(row[2]).rstrip())
                    list_item["n_pdp"] = int(str(row[3]).rstrip())
                    list_item["n_confirm"] = int(str(row[4]).rstrip())
                    list_item["n_meninggal"] = int(str(row[5]).rstrip())
                    list_item["n_sembuh"] = int(str(row[6]).rstrip())
                    list_item["last_update"] = "N/A"
                    kabkota = KabupatenKota.select().where(
                        KabupatenKota.prov_id == propinsi,
                        KabupatenKota.nama == str(row[1]).rstrip(),
                    )

                    if kabkota.count() < 1:
                        kabkota = KabupatenKota.create(
                            prov_id=propinsi, nama=str(row[1]).rstrip()
                        )
                    else:
                        kabkota = kabkota.get()
                    datum = Data.select().where(
                        Data.kabupaten == kabkota,
                        Data.last_update == datetime.datetime.now(),
                    )
                    if datum.count() < 1:
                        datum = Data.create(
                            kabupaten=kabkota,
                            n_odp=int(str(row[2]).rstrip()),
                            n_pdp=int(str(row[3]).rstrip()),
                            n_confirm=int(str(row[4]).rstrip()),
                            n_meninggal=int(str(row[5]).rstrip()),
                            n_sembuh=int(str(row[6]).rstrip()),
                            last_update=datetime.datetime.now(),
                        )
                    output["result"].append(list_item)

                i = i + 1

    return output
