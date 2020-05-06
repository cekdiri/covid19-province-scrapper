import datetime

import dateparser
import pandas as pd
import requests
from lxml import html, etree
from peewee import fn

from models import Province, KabupatenKota, Data


def scrape():
    prov = __name__.split(".")[-1]
    propinsi = Province.select().where(Province.nama_prov == "Jawa Tengah")
    if propinsi.count() < 1:
        propinsi = Province.create(nama_prov="Jawa Tengah", alias=prov)
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
    link = "https://corona.jatengprov.go.id/data"
    output = {}
    output["result"] = []
    with requests.session() as s:
        r = s.get(link, verify=True)
        tree = html.fromstring(r.text)
        _last_update = tree.xpath("//section[5]/div/div/div[1]/div/p/text()")[0].strip()

        table_elem = tree.xpath("//section[5]/div/div/div[2]/div/div/table")[0]
        table_str = etree.tostring(table_elem)

        if table_str is not None and table_str != "":
            res = []

            df = pd.read_html(table_str)[0]
            df["positif"] = df["Positif: Sembuh"] + df["Positif: Meninggal"] + df["Positif: Dirawat"]
            table = df.to_dict("records")

            for row in table:
                list_item = {}
                list_item["provinsi"] = "Jawa Tengah"
                list_item["kode_kab_kota"] = "N/A"
                list_item["kab_kota"] = row["Kabupaten/Kota"]
                list_item["kecamatan"] = "N/A"
                list_item["populasi"] = "N/A"
                list_item["lat_kab_kota"] = "N/A"
                list_item["long_kab_kota"] = "N/A"
                list_item["n_odr"] = "N/A"
                list_item["n_otg"] = "N/A"
                list_item["n_odp"] = row["ODP: Proses"]
                list_item["n_pdp"] = row["PDP: Dirawat"]
                list_item["n_confirm"] = row["positif"]
                list_item["n_meninggal"] = row["Positif: Meninggal"]
                list_item["n_sembuh"] = row["Positif: Sembuh"]
                list_item["last_update"] = _last_update

                kabkota = KabupatenKota.select().where(
                    KabupatenKota.prov_id == propinsi,
                    KabupatenKota.nama == list_item["kab_kota"],
                )

                if kabkota.count() < 1:
                    kabkota = KabupatenKota.create(
                        prov_id=propinsi, nama=list_item["kab_kota"]
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
                        n_pdp=list_item["n_pdp"],
                        n_confirm=list_item["n_confirm"],
                        n_meninggal=list_item["n_meninggal"],
                        n_sembuh=list_item["n_sembuh"],
                        last_update=dateparser.parse(_last_update),
                    )
                output["result"].append(list_item)

    return output
