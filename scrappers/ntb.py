import datetime

import dateparser
import requests
from bs4 import BeautifulSoup as soup
from peewee import fn

from models import Province, KabupatenKota, Data


def scrape():
    prov = __name__.split(".")[-1]
    propinsi = Province.select().where(Province.nama_prov == "Nusa Tenggara Barat")
    if propinsi.count() < 1:
        propinsi = Province.create(nama_prov="Nusa Tenggara Barat", alias=prov)
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

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "cookie": "XSRF-TOKEN=eyJpdiI6IjJGSjNJWmxJS1AzNExHQ1poVDZPeWc9PSIsInZhbHVlIjoiTVEvWTVSWHZJSUtyY0RaalFPa2tzZW1hWmJYN0ZucGtEMXFtNGRRN3RLQXloVkxwNC90VEZMZHozYk1kV1cvLyIsIm1hYyI6ImVlM2NjOTg4YTA2YzMxZjllZGE3MGM0Njk1YTJmZGU1Nzc3ZGE4MmM1MWRlNTg4YWFjZWQ4MWQxZmUzMzkyNzEifQ%3D%3D; laravel_session=eyJpdiI6InN3a2JkdGJPcWMvNmVxbmxBZGxCK2c9PSIsInZhbHVlIjoiM1dwZmdmUHdNY3RwWG9oVXJqM2dYQmZSWnlEakY3TkVNZ2Mra21RY3hLN3V0UGMwQWxVbzhSbU5NNjR0aHdyeiIsIm1hYyI6ImQxNzYyMWI2MjhkMDRlYTY1Mjc4NDFhMTRkMzZiNDliNjdkY2NiNDkxZTY1NTRjZTIxZGVjZGE1YjkzZmUyZWYifQ%3D%3D",
        "referer": "https://corona.ntbprov.go.id/",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
    }

    link = "https://corona.ntbprov.go.id/list-data"
    output = {}
    output["result"] = []
    with requests.session() as s:

        r = s.get(link, verify=False, headers=headers)
        data = r.text
        url = soup(data, "lxml")

        table = url.find("table", attrs={"class": "table table-bordered table-striped"})
        # print(table)

        if table is not None:
            res = []

            th = table.find("th")
            info_date = th.text.replace("\n", "").replace("  ", "")
            pos_l = info_date.find(",")
            pos_r = info_date.rfind("Pukul")
            _last_update = info_date[pos_l + 1 : pos_r]

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
                        list_item["provinsi"] = "Nusa Tenggara Barat"
                        list_item["kode_kab_kota"] = "N/A"
                        list_item["kab_kota"] = (
                            str(row[0])
                            .replace("\n", "")
                            .replace("               ", " ")
                        )
                        list_item["kecamatan"] = "N/A"
                        list_item["populasi"] = "N/A"
                        list_item["lat_kab_kota"] = "N/A"
                        list_item["long_kab_kota"] = "N/A"
                        list_item["n_odr"] = "N/A"
                        list_item["n_otg"] = int(str(row[5]).rstrip())
                        list_item["n_odp"] = int(str(row[8]).rstrip())
                        list_item["n_pdp"] = int(str(row[11]).rstrip())
                        list_item["n_confirm"] = int(str(row[14]).rstrip())
                        list_item["n_meninggal"] = int(str(row[16]).rstrip())
                        list_item["n_sembuh"] = int(str(row[17]).rstrip())
                        list_item["last_update"] = _last_update
                        # print(list_item)
                        kabkota = KabupatenKota.select().where(
                            KabupatenKota.prov_id == propinsi,
                            KabupatenKota.nama == row[1],
                        )

                        if kabkota.count() < 1:
                            kabkota = KabupatenKota.create(
                                prov_id=propinsi,
                                nama=str(row[0])
                                .replace("\n", "")
                                .replace("               ", " "),
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
                                n_otg=int(str(row[5]).rstrip()),
                                n_odp=int(str(row[8]).rstrip()),
                                n_pdp=int(str(row[11]).rstrip()),
                                n_confirm=int(str(row[14]).rstrip()),
                                n_meninggal=int(str(row[16]).rstrip()),
                                n_sembuh=int(str(row[17]).rstrip()),
                                last_update=dateparser.parse(_last_update),
                            )
                        output["result"].append(list_item)
                i = i + 1
    return output
