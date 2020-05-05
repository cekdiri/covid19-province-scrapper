import datetime

import dateparser
import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
from peewee import fn

from models import Province, KabupatenKota, Data


def scrape():
    prov = __name__.split(".")[-1]
    propinsi = Province.select().where(Province.nama_prov == "Bangka Belitung")
    if propinsi.count() < 1:
        propinsi = Province.create(nama_prov="Bangka Belitung", alias=prov)
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
    link = "http://covid19.babelprov.go.id/"
    output = {}
    output["result"] = []

    with requests.session() as s:

        r = s.get(link, verify=False)
        data = r.text
        # print(data)
        url = soup(data, "lxml")

        title = url.find("span", attrs={"class": "covid__date"}).text
        pos = str(title).rfind(", ")
        _last_update = str(title)[pos + 1 :].strip()
        parsed_date = dateparser.parse(_last_update, date_formats=["%d %B %Y - %H.%M WIB"])

        table = url.find("table", attrs={"class": "covidkab"})

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
                    list_item["provinsi"] = "Bangka Belitung"
                    list_item["kode_kab_kota"] = "N/A"
                    list_item["kab_kota"] = row[0]
                    list_item["kecamatan"] = "N/A"
                    list_item["populasi"] = "N/A"
                    list_item["lat_kab_kota"] = "N/A"
                    list_item["long_kab_kota"] = "N/A"
                    list_item["n_odr"] = "N/A"
                    list_item["n_otg"] = int(str(row[1]).rstrip())
                    list_item["n_odp"] = int(str(row[3]).rstrip())
                    list_item["n_pdp"] = int(str(row[4]).rstrip())
                    list_item["n_confirm"] = int(str(row[2]).rstrip())
                    list_item["n_meninggal"] = "N/A"
                    list_item["n_sembuh"] = "N/A"
                    list_item["last_update"] = _last_update
                    # print(list_item)
                    kabkota = KabupatenKota.select().where(
                        KabupatenKota.prov_id == propinsi, KabupatenKota.nama == row[0]
                    )

                    if kabkota.count() < 1:
                        kabkota = KabupatenKota.create(prov_id=propinsi, nama=row[0])
                    else:
                        kabkota = kabkota.get()

                    datum = Data.select().where(
                        Data.kabupaten == kabkota,
                        Data.last_update == parsed_date,
                    )
                    if datum.count() < 1:
                        datum = Data.create(
                            kabupaten=kabkota,
                            n_otg=int(str(row[1]).rstrip()),
                            n_odp=int(str(row[3]).rstrip()),
                            n_pdp=int(str(row[4]).rstrip()),
                            n_confirm=int(str(row[2]).rstrip()),
                            last_update=parsed_date,
                        )
                    output["result"].append(list_item)

                i = i + 1

    return output
