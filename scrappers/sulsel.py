import datetime
import re

import dateparser
import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
from peewee import fn

from models import Province, KabupatenKota, Data


def scrape():
    prov = __name__.split(".")[-1]
    propinsi = Province.select().where(Province.nama_prov == "Sulawesi Selatan")
    if propinsi.count() < 1:
        propinsi = Province.create(nama_prov="Sulawesi Selatan", alias=prov)
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
    link = "https://covid19.sulselprov.go.id"
    output = {}
    output["result"] = []

    with requests.session() as s:

        r = s.get(link, verify=False)
        data = r.text
        # print(data)
        data = re.sub(r"<!--", "", data)
        data = re.sub(r"-->", "", data)
        url = soup(data, "lxml")

        title = url.find("h4", attrs={"class": "text-danger"}).text
        pos = str(title).rfind("-")
        _last_update = str(title)[pos + 1 :]

        table = url.find("table", attrs={"class": "table table-striped"})

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
                    list_item["provinsi"] = "Sulawesi Selatan"
                    list_item["kode_kab_kota"] = "N/A"
                    list_item["kab_kota"] = row[1]
                    list_item["kecamatan"] = "N/A"
                    list_item["populasi"] = "N/A"
                    list_item["lat_kab_kota"] = "N/A"
                    list_item["long_kab_kota"] = "N/A"
                    list_item["n_odr"] = "N/A"
                    list_item["n_otg"] = "N/A"
                    list_item["n_odp"] = int(str(row[2]).rstrip())
                    list_item["n_pdp"] = int(str(row[3]).rstrip())
                    list_item["n_confirm"] = int(str(row[4]).rstrip())
                    list_item["n_meninggal"] = "N/A"
                    list_item["n_sembuh"] = "N/A"
                    list_item["last_update"] = _last_update
                    # print(list_item)
                    output["result"].append(list_item)

                    kabkota = KabupatenKota.select().where(
                        KabupatenKota.prov_id == propinsi, KabupatenKota.nama == row[1]
                    )

                    if kabkota.count() < 1:
                        kabkota = KabupatenKota.create(prov_id=propinsi, nama=row[1])
                    else:
                        kabkota = kabkota.get()

                    datum = Data.select().where(
                        Data.kabupaten == kabkota,
                        Data.last_update == dateparser.parse(_last_update),
                    )
                    if datum.count() < 1:
                        datum = Data.create(
                            kabupaten=kabkota,
                            n_odp=int(str(row[2]).rstrip()),
                            n_pdp=int(str(row[3]).rstrip()),
                            n_confirm=int(str(row[4]).rstrip()),
                            last_update=dateparser.parse(_last_update),
                        )
                i = i + 1

    return output
