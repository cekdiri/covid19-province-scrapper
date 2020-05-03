import datetime

import dateparser
import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
from peewee import fn
from selenium import webdriver

from models import Province, KabupatenKota, Data


def scrape():
    prov = __name__.split(".")[-1]
    propinsi = Province.select().where(
        Province.nama_prov == "Daerah Istimewa Yogyakarta"
    )
    if propinsi.count() < 1:
        propinsi = Province.create(nama_prov="Daerah Istimewa Yogyakarta", alias=prov)
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
    # konfigurasi chromedriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1420,1080")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    browser = webdriver.Chrome(chrome_options=chrome_options)

    hidden = "/html/body/div[2]/div[2]/div/div/form/input[1]"
    kodepos = '//*[@id="fname"]'
    button = "/html/body/div[2]/div[2]/div/div/form/button"

    kodepos_df = pd.read_csv("Data_KodePos_Kecamatan_DIY.csv", delimiter=";")

    output = {}
    output["result"] = []
    for index, row in kodepos_df.iterrows():
        # konfigurasi base URL
        link = "https://sebaran-covid19.jogjaprov.go.id/kodepos"
        browser.get(link)
        kode_pos = str(row["kode_pos"])

        e = browser.find_element_by_xpath(hidden).get_attribute("value")
        e = browser.find_element_by_xpath(kodepos)
        e.send_keys(kode_pos)
        e = browser.find_element_by_xpath(button)
        e.click()
        # time.sleep(5)

        data = browser.page_source
        # print(data)
        url = soup(data, "lxml")

        odp = url.find("b", {"id": "odp"})
        pdp = url.find("b", {"id": "pdp"})
        positif = url.find("b", {"id": "positif"})
        last_update_blok = url.find("div", {"class": "dataupdate"})
        populasi = url.find("b", {"id": "populasi"})
        if populasi is None:
            populasi = url.find("strong", {"id": "populasi"})

        for item in last_update_blok.contents:
            if item.name == "p":
                if item.has_attr("style") == False:
                    _last_update = item.text.replace("Data Update ", "").rstrip()

        list_item = {}
        list_item["provinsi"] = "Daerah Istimewa Yogyakarta"

        list_item["kode_kab_kota"] = str(row["kode_wilayah"])
        list_item["kab_kota"] = str(row["kabupaten_kota"])
        list_item["kecamatan"] = str(row["nama_kecamatan"])
        list_item["populasi"] = str(populasi.text).rstrip()
        list_item["lat_kab_kota"] = "N/A"
        list_item["long_kab_kota"] = "N/A"
        list_item["n_odr"] = "N/A"
        list_item["n_otg"] = "N/A"
        list_item["n_odp"] = int(str(odp.text).rstrip())
        list_item["n_pdp"] = int(str(pdp.text).rstrip())
        list_item["n_confirm"] = int(str(positif.text).rstrip())
        list_item["n_meninggal"] = "N/A"
        list_item["n_sembuh"] = "N/A"
        list_item["last_update"] = _last_update

        kabkota = KabupatenKota.select().where(
            KabupatenKota.prov_id == propinsi,
            KabupatenKota.nama == str(row["kabupaten_kota"]),
        )

        if kabkota.count() < 1:
            kabkota = KabupatenKota.create(
                prov_id=propinsi,
                nama=str(row["kabupaten_kota"]),
                kode=str(row["kode_wilayah"]),
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
                n_odp=int(str(odp.text).rstrip()),
                n_pdp=int(str(pdp.text).rstrip()),
                n_confirm=int(str(positif.text).rstrip()),
                last_update=dateparser.parse(_last_update),
            )
        output["result"].append(list_item)
    browser.stop_client()
    browser.close()
    browser.quit()

    return output

