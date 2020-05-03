import datetime

import dateparser
import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
from peewee import fn

from models import Province, KabupatenKota, Data


def scrape():
    prov = __name__.split(".")[-1]
    propinsi = Province.select().where(Province.nama_prov == "Bali")
    if propinsi.count() < 1:
        propinsi = Province.create(nama_prov="Bali", alias=prov)
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
    link = "https://pendataan.baliprov.go.id/"
    output = {}
    output["result"] = []
    with requests.session() as s:

        r = s.get(link, verify=True)
        data = r.text
        url = soup(data, "lxml")

        con = url.find_all("div", attrs={"card-header"})
        title = con[6].find("h3").text
        pos = str(title).rfind("Dengan ")
        _last_update = str(title)[pos + 7 :]

        table = url.find("table", attrs={"class": "table"})
        # print(table)

        if table is not None:
            res = []
            table_rows = table.find_all("tr")
            num_rows = len(table_rows)

            i = 0
            for tr in table_rows:
                td = tr.find_all("td")
                row = [tr.text.strip() for tr in td if tr.text.strip()]
                # print(row)
                if i >= 1 and i < num_rows - 1:
                    if row:
                        list_item = {}
                        list_item["provinsi"] = "Bali"
                        list_item["kode_kab_kota"] = "N/A"
                        list_item["kab_kota"] = row[0]
                        list_item["kecamatan"] = "N/A"
                        list_item["populasi"] = "N/A"
                        list_item["lat_kab_kota"] = "N/A"
                        list_item["long_kab_kota"] = "N/A"
                        list_item["n_odr"] = "N/A"
                        list_item["n_otg"] = "N/A"
                        list_item["n_odp"] = "N/A"
                        list_item["n_pdp"] = int(str(row[7]).rstrip())
                        list_item["n_confirm"] = int(str(row[6]).rstrip())
                        list_item["n_meninggal"] = int(str(row[9]).rstrip())
                        list_item["n_sembuh"] = int(str(row[8]).rstrip())
                        list_item["last_update"] = _last_update
                        # print(list_item)
                        kabkota = KabupatenKota.select().where(
                            KabupatenKota.prov_id == propinsi,
                            KabupatenKota.nama == row[0],
                        )

                        if kabkota.count() < 1:
                            kabkota = KabupatenKota.create(
                                prov_id=propinsi, nama=row[0]
                            )
                        else:
                            kabkota = kabkota.get()

                        datum = Data.select().where(
                            Data.kabupaten == kabkota,
                            Data.last_update == dateparser.parse(_last_update),
                        )
                        if datum.count() < 1:
                            datum = Data.create(
                                kabupaten=kabkota,
                                n_pdp=int(str(row[7]).rstrip()),
                                n_confirm=int(str(row[6]).rstrip()),
                                n_meninggal=int(str(row[9]).rstrip()),
                                n_sembuh=int(str(row[8]).rstrip()),
                                last_update=dateparser.parse(_last_update),
                            )
                        output["result"].append(list_item)
                i = i + 1
    return output
