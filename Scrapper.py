import json
from bs4 import BeautifulSoup as soup
import requests
import datetime
import re

import certifi

import selenium
from selenium import webdriver
import pandas as pd
import time
import peewee as pw
from peewee import fn
import dateparser
from models import Province, KabupatenKota, Data


class Scrapper:

    def get_pos(str_lf,str_rg,text):
        left = text.find(str_lf)
        right = text.rfind(str_rg)

        return left, right


    def scrapper(prov):
        if prov=='jatim':
            propinsi = Province.select().where(Province.nama_prov=='Jawa Timur')
            if propinsi.count() < 1:
                propinsi =Province.create(nama_prov='Jawa Timur', alias=prov)
            else:
                propinsi  = propinsi.get()
            sekarang = datetime.datetime.now().date()
            try:
                result = list(Data.select().join(Province).where(fn.date_trunc('day', Data.last_update) == sekarang), Province.alias==prov)
            except:
                result = []
            if len(result) > 0:
                return result
            link = 'http://covid19dev.jatimprov.go.id/xweb/draxi'
            output = {}
            output['result'] = []        
            with requests.session() as s:
                r = s.get(link,verify=True)
                data = r.text
                url = soup(data,"lxml")

                script = url.find_all('script')
                json_data = ''
                for item in script:
                    if re.search(r'datakabupaten=(\[{.*\}\])',str(item)):
                        var_data = re.findall(r'datakabupaten=(\[{.*\}\])',str(item))
                        json_data = json.loads(str(var_data[0]))


                for data in json_data:
                    list_item = {}
                    list_item['provinsi'] = 'Jawa Timur'                
                    list_item['kode_kab_kota'] = data['kode']
                    list_item['kab_kota'] = data['kabko']
                    list_item['kecamatan'] = 'N/A'
                    list_item['populasi'] = 'N/A'
                    list_item['lat_kab_kota'] = data['lat']
                    list_item['long_kab_kota'] = data['lon']                
                    list_item['n_odr'] = data['odr']
                    list_item['n_otg'] = data['otg']
                    list_item['n_odp'] = data['odp']
                    list_item['n_pdp'] = data['pdp']
                    list_item['n_confirm'] = data['confirm']
                    list_item['n_meninggal'] = data['meninggal']
                    list_item['n_sembuh'] = data['sembuh']
                    list_item['last_update'] = data['updated_at']

                    kabkota = KabupatenKota.select().where(KabupatenKota.prov_id==propinsi, 
                        KabupatenKota.nama==data['kabko'], KabupatenKota.kode==data['kode'])

                    if kabkota.count() < 1:
                        kabkota =KabupatenKota.create(prov_id=propinsi, 
                            nama=data['kabko'], kode=data['kode'],
                            lat=data['lat'], lon=data['lon'],populasi='')
                    else:
                        kabkota  = kabkota.get()

                    datum = Data.select().where(Data.kabupaten==kabkota, Data.last_update==dateparser.parse(data['updated_at']))
                    if datum.count() < 1:
                        datum = Data.create(
                            kabupaten=kabkota,
                            n_odr=data['odr'],
                            n_otg=data['otg'],
                            n_odp=data['odp'],
                            n_pdp=data['pdp'],
                            n_confirm=data['confirm'],
                            n_meninggal=data['meninggal'],
                            n_sembuh=data['sembuh'],
                            last_update=dateparser.parse(data['updated_at'])
                        )

                    output['result'].append(list_item)

            return output 

        elif prov=='aceh':
            propinsi = Province.select().where(Province.nama_prov=='Aceh')
            if propinsi.count() < 1:
                propinsi =Province.create(nama_prov='Aceh', alias=prov)
            else:
                propinsi  = propinsi.get()
            sekarang = datetime.datetime.now().date()
            try:
                result = list(Data.select().join(Province).where(fn.date_trunc('day', Data.last_update) == sekarang), Province.alias==prov)
            except:
                result = []
            if len(result) > 0:
                return result

            link = 'https://covid.bravo.siat.web.id/json/peta'
            output = {}
            output['result'] = []        
            with requests.session() as s:
                r = s.get(link,verify=True)
                data = r.text
                json_data = json.loads(data)
                #print(json_data)
                for data in json_data:
                    list_item = {}
                    list_item['provinsi'] = 'Aceh'                
                    list_item['kode_kab_kota'] = 'N/A'
                    list_item['kab_kota'] = data['namaKabupaten']
                    list_item['kecamatan'] = 'N/A'
                    list_item['populasi'] = 'N/A'
                    list_item['lat_kab_kota'] = data['latitude']
                    list_item['long_kab_kota'] = data['longitude']                
                    list_item['n_odr'] = 'N/A'
                    list_item['n_otg'] = 'N/A'
                    list_item['n_odp'] = data['odp']
                    list_item['n_pdp'] = data['pdp']
                    list_item['n_confirm'] = data['positif']
                    list_item['n_meninggal'] = data['positifMeninggal']
                    list_item['n_sembuh'] = data['positifSembuh']
                    list_item['last_update'] = data['updateDate']

                    kabkota = KabupatenKota.select().where(KabupatenKota.prov_id==propinsi, 
                        KabupatenKota.nama==data['namaKabupaten'])

                    if kabkota.count() < 1:
                        kabkota =KabupatenKota.create(prov_id=propinsi, 
                            nama=data['namaKabupaten'],
                            lat=data['latitude'], lon=data['longitude'])
                    else:
                        kabkota  = kabkota.get()
                    datum = Data.select().where(Data.kabupaten==kabkota, Data.last_update==dateparser.parse(data['updateDate']))
                    if datum.count() < 1:
                        datum = Data.create(
                            kabupaten=kabkota,
                            n_odp=data['odp'],
                            n_pdp=data['pdp'],
                            n_confirm=data['positif'],
                            n_meninggal=data['positifMeninggal'],
                            n_sembuh=data['positifSembuh'],
                            last_update=dateparser.parse(data['updateDate'])
                        )
                    output['result'].append(list_item)

            return output 

        elif prov=='kalsel':
            propinsi = Province.select().where(Province.nama_prov=='Kalimantan Selatan')
            if propinsi.count() < 1:
                propinsi =Province.create(nama_prov='Kalimantan Selatan', alias=prov)
            else:
                propinsi  = propinsi.get()
            sekarang = datetime.datetime.now().date()
            try:
                result = list(Data.select().join(Province).where(fn.date_trunc('day', Data.last_update) == sekarang), Province.alias==prov)
            except:
                result = []
            if len(result) > 0:
                return result

            link = 'https://corona.kalselprov.go.id/cov_map'
            output = {}
            output['result'] = []        
            with requests.session() as s:
                r = s.get(link,verify=True)
                data = r.text
                json_data = json.loads(data)
                #print(json_data)
                for data in json_data:
                    list_item = {}
                    list_item['provinsi'] = 'Kalimantan Selatan'                
                    list_item['kode_kab_kota'] = data['code']
                    list_item['kab_kota'] = data['name']
                    list_item['kecamatan'] = 'N/A'
                    list_item['populasi'] = 'N/A'
                    list_item['lat_kab_kota'] = 'N/A'
                    list_item['long_kab_kota'] = 'N/A'              
                    list_item['n_odr'] = 'N/A'
                    list_item['n_otg'] = 'N/A'
                    list_item['n_odp'] = data['cov_odp_count']
                    list_item['n_pdp'] = data['cov_pdp_count']
                    list_item['n_confirm'] = data['cov_positive_count']
                    list_item['n_meninggal'] = data['cov_died_count']
                    list_item['n_sembuh'] = data['cov_recovered_count']
                    list_item['last_update'] = 'N/A'
                    kabkota = KabupatenKota.select().where(KabupatenKota.prov_id==propinsi, 
                        KabupatenKota.nama==data['name'])

                    if kabkota.count() < 1:
                        kabkota =KabupatenKota.create(prov_id=propinsi, 
                            nama=data['name'], kode=data['code'])
                    else:
                        kabkota  = kabkota.get()
                    datum = Data.select().where(Data.kabupaten==kabkota, Data.last_update==datetime.datetime.now())
                    if datum.count() < 1:
                        datum = Data.create(
                            kabupaten=kabkota,
                            n_odp=data['cov_odp_count'],
                            n_pdp=data['cov_pdp_count'],
                            n_confirm=data['cov_positive_count'],
                            n_meninggal=data['cov_died_count'],
                            n_sembuh=data['cov_recovered_count'],
                            last_update=datetime.datetime.now()
                        )
                    output['result'].append(list_item)

            return output 

        elif prov=='sumut':
            propinsi = Province.select().where(Province.nama_prov=='Kalimantan Selatan')
            if propinsi.count() < 1:
                propinsi =Province.create(nama_prov='Kalimantan Selatan', alias=prov)
            else:
                propinsi  = propinsi.get()
            sekarang = datetime.datetime.now().date()
            try:
                result = list(Data.select().join(Province).where(fn.date_trunc('day', Data.last_update) == sekarang), Province.alias==prov)
            except:
                result = []
            if len(result) > 0:
                return result
            link = 'http://covid19.sumutprov.go.id/home'
            output = {}
            output['result'] = []        
            with requests.session() as s:
                r = s.get(link,verify=True)
                data = r.text
                data = re.sub(r"<!--", "", data)
                data = re.sub(r"-->", "", data)
                url = soup(data,"lxml")

                table = url.find('table', attrs={'class':'table table-striped table-bordered table-responsive'})

                if table is not None:
                    res = []
                    table_rows = table.find_all('tr')

                    num_rows = len(table_rows)
                    #print(num_rows)

                    i=0
                    for tr in table_rows:
                        td = tr.find_all('td')
                        row = [tr.text.strip() for tr in td if tr.text.strip()]
                        #print(row)

                        if i>=1 and i<num_rows-1:

                            list_item = {}
                            list_item['provinsi'] = 'Sumatera Utara'                
                            list_item['kode_kab_kota'] = "N/A"
                            list_item['kab_kota'] = str(row[1]).rstrip()

                            list_item['kecamatan'] = 'N/A'
                            list_item['populasi'] = 'N/A'
                            list_item['lat_kab_kota'] = 'N/A'
                            list_item['long_kab_kota'] = 'N/A'                
                            list_item['n_odr'] = 'N/A'
                            list_item['n_otg'] = 'N/A'
                            list_item['n_odp'] = int(str(row[2]).rstrip())
                            list_item['n_pdp'] = int(str(row[3]).rstrip())
                            list_item['n_confirm'] = int(str(row[4]).rstrip())
                            list_item['n_meninggal'] = int(str(row[5]).rstrip())
                            list_item['n_sembuh'] = int(str(row[6]).rstrip())
                            list_item['last_update'] = 'N/A'
                            kabkota = KabupatenKota.select().where(KabupatenKota.prov_id==propinsi, 
                                KabupatenKota.nama==str(row[1]).rstrip())

                            if kabkota.count() < 1:
                                kabkota =KabupatenKota.create(prov_id=propinsi, 
                                    nama=str(row[1]).rstrip())
                            else:
                                kabkota  = kabkota.get()
                            datum = Data.select().where(Data.kabupaten==kabkota, Data.last_update==datetime.datetime.now())
                            if datum.count() < 1:
                                datum = Data.create(
                                    kabupaten=kabkota,
                                    n_odp=int(str(row[2]).rstrip()),
                                    n_pdp=int(str(row[3]).rstrip()),
                                    n_confirm=int(str(row[4]).rstrip()),
                                    n_meninggal=int(str(row[5]).rstrip()),
                                    n_sembuh=int(str(row[6]).rstrip()),
                                    last_update=datetime.datetime.now()
                                )
                            output['result'].append(list_item)

                        
                        i=i+1

            return output 

        elif prov=='diy':
            propinsi = Province.select().where(Province.nama_prov=='Daerah Istimewa Yogyakarta')
            if propinsi.count() < 1:
                propinsi =Province.create(nama_prov='Daerah Istimewa Yogyakarta', alias=prov)
            else:
                propinsi  = propinsi.get()
            sekarang = datetime.datetime.now().date()
            try:
                result = list(Data.select().join(Province).where(fn.date_trunc('day', Data.last_update) == sekarang), Province.alias==prov)
            except:
                result = []
            if len(result) > 0:
                return result
            # konfigurasi chromedriver
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--window-size=1420,1080')
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')

            browser = webdriver.Chrome(chrome_options=chrome_options)

            hidden = '/html/body/div[2]/div[2]/div/div/form/input[1]'
            kodepos = '//*[@id="fname"]'
            button = '/html/body/div[2]/div[2]/div/div/form/button'

            kodepos_df = pd.read_csv("Data_KodePos_Kecamatan_DIY.csv",delimiter=';')

            output = {}
            output['result'] = []        
            for index, row in kodepos_df.iterrows():
                # konfigurasi base URL
                link = 'https://sebaran-covid19.jogjaprov.go.id/kodepos'
                browser.get(link)
                kode_pos = str(row['kode_pos'])

                e = browser.find_element_by_xpath(hidden).get_attribute("value")
                e = browser.find_element_by_xpath(kodepos)
                e.send_keys(kode_pos)
                e = browser.find_element_by_xpath(button)
                e.click()
                #time.sleep(5)

                data = browser.page_source
                #print(data)
                url = soup(data,"lxml")

                odp = url.find("b",{"id":"odp"})
                pdp = url.find("b",{"id":"pdp"})
                positif = url.find("b",{"id":"positif"})
                last_update_blok = url.find("div",{"class":"dataupdate"})
                populasi = url.find("b",{"id":"populasi"})
                if populasi is None:
                    populasi = url.find("strong",{"id":"populasi"})

                for item in last_update_blok.contents:
                    if item.name=='p':
                        if item.has_attr('style')==False:
                            _last_update = item.text.replace('Data Update ','').rstrip()



                list_item = {}
                list_item['provinsi'] = 'Daerah Istimewa Yogyakarta'

                list_item['kode_kab_kota'] = str(row['kode_wilayah'])
                list_item['kab_kota'] = str(row['kabupaten_kota'])
                list_item['kecamatan'] = str(row['nama_kecamatan'])
                list_item['populasi'] = str(populasi.text).rstrip()
                list_item['lat_kab_kota'] = 'N/A'
                list_item['long_kab_kota'] = 'N/A'
                list_item['n_odr'] = 'N/A'
                list_item['n_otg'] = 'N/A'
                list_item['n_odp'] = int(str(odp.text).rstrip())
                list_item['n_pdp'] = int(str(pdp.text).rstrip())
                list_item['n_confirm'] = int(str(positif.text).rstrip())
                list_item['n_meninggal'] = 'N/A'
                list_item['n_sembuh'] = 'N/A'
                list_item['last_update'] = _last_update

                kabkota = KabupatenKota.select().where(KabupatenKota.prov_id==propinsi, 
                    KabupatenKota.nama==str(row['kabupaten_kota']))

                if kabkota.count() < 1:
                    kabkota =KabupatenKota.create(prov_id=propinsi, 
                        nama=str(row['kabupaten_kota']), kode=str(row['kode_wilayah']))
                else:
                    kabkota  = kabkota.get()
                datum = Data.select().where(Data.kabupaten==kabkota, Data.last_update==dateparser.parse(_last_update))
                if datum.count() < 1:
                    datum = Data.create(
                        kabupaten=kabkota,
                        n_odp=int(str(odp.text).rstrip()),
                        n_pdp=int(str(pdp.text).rstrip()),
                        n_confirm=int(str(positif.text).rstrip()),
                        last_update=dateparser.parse(_last_update)
                    )
                output['result'].append(list_item)
            browser.stop_client()
            browser.close()
            browser.quit()

            return output   

        elif prov=='sulsel':
            propinsi = Province.select().where(Province.nama_prov=='Sulawesi Selatan')
            if propinsi.count() < 1:
                propinsi =Province.create(nama_prov='Sulawesi Selatan', alias=prov)
            else:
                propinsi  = propinsi.get()
            sekarang = datetime.datetime.now().date()
            try:
                result = list(Data.select().join(Province).where(fn.date_trunc('day', Data.last_update) == sekarang), Province.alias==prov)
            except:
                result = []
            if len(result) > 0:
                return result
            link = 'https://covid19.sulselprov.go.id'
            output = {}
            output['result'] = []   

            with requests.session() as s:

                r = s.get(link,verify=False)
                data = r.text 
                #print(data)
                data = re.sub(r"<!--", "", data)
                data = re.sub(r"-->", "", data)
                url = soup(data,"lxml")

                title = url.find('h4',attrs={'class':'text-danger'}).text
                pos = str(title).rfind('-')
                _last_update = str(title)[pos+1:]

                table = url.find('table', attrs={'class':'table table-striped'})

                if table is not None:
                    res = []
                    table_rows = table.find_all('tr')

                    num_rows = len(table_rows)
                    #print(num_rows)

                    i = 0

                    for tr in table_rows:
                        td = tr.find_all('td')
                        row = [tr.text.strip() for tr in td if tr.text.strip()]
                        #print(row)
                        if i>=1 and i<num_rows-1:

                            list_item = {}
                            list_item['provinsi'] = 'Sulawesi Selatan'
                            list_item['kode_kab_kota'] = 'N/A'
                            list_item['kab_kota'] = row[1] 
                            list_item['kecamatan'] = 'N/A'
                            list_item['populasi'] = 'N/A'
                            list_item['lat_kab_kota'] = 'N/A'
                            list_item['long_kab_kota'] = 'N/A'
                            list_item['n_odr'] = 'N/A'
                            list_item['n_otg'] = 'N/A'
                            list_item['n_odp'] = int(str(row[2]).rstrip())
                            list_item['n_pdp'] = int(str(row[3]).rstrip())
                            list_item['n_confirm'] = int(str(row[4]).rstrip())
                            list_item['n_meninggal'] = 'N/A'
                            list_item['n_sembuh'] = 'N/A'
                            list_item['last_update'] = _last_update
                            #print(list_item)
                            output['result'].append(list_item)

                            kabkota = KabupatenKota.select().where(KabupatenKota.prov_id==propinsi, 
                                KabupatenKota.nama==row[1])

                            if kabkota.count() < 1:
                                kabkota =KabupatenKota.create(prov_id=propinsi, 
                                    nama=row[1])
                            else:
                                kabkota  = kabkota.get()

                            datum = Data.select().where(Data.kabupaten==kabkota, Data.last_update==dateparser.parse(_last_update))
                            if datum.count() < 1:
                                datum = Data.create(
                                    kabupaten=kabkota,
                                    n_odp=int(str(row[2]).rstrip()),
                                    n_pdp=int(str(row[3]).rstrip()),
                                    n_confirm=int(str(row[4]).rstrip()),
                                    last_update=dateparser.parse(_last_update)
                                )
                        i=i+1

            return output

        elif prov=='babel':
            propinsi = Province.select().where(Province.nama_prov=='Bangka Belitung')
            if propinsi.count() < 1:
                propinsi =Province.create(nama_prov='Bangka Belitung', alias=prov)
            else:
                propinsi  = propinsi.get()
            sekarang = datetime.datetime.now().date()
            try:
                result = list(Data.select().join(Province).where(fn.date_trunc('day', Data.last_update) == sekarang), Province.alias==prov)
            except:
                result = []
            if len(result) > 0:
                return result
            link = 'http://covid19.babelprov.go.id/'
            output = {}
            output['result'] = []   

            with requests.session() as s:

                r = s.get(link,verify=False)
                data = r.text 
                #print(data)
                url = soup(data,"lxml")

                title = url.find('span',attrs={'class':'covid__date'}).text
                pos = str(title).rfind(', ')
                _last_update = str(title)[pos+1:]

                table = url.find('table', attrs={'class':'covidkab'})

                if table is not None:
                    res = []
                    table_rows = table.find_all('tr')

                    num_rows = len(table_rows)
                    #print(num_rows)

                    i = 0

                    for tr in table_rows:
                        td = tr.find_all('td')
                        row = [tr.text.strip() for tr in td if tr.text.strip()]
                        #print(row)
                        if i>=1 and i<num_rows-1:

                            list_item = {}
                            list_item['provinsi'] = 'Bangka Belitung'
                            list_item['kode_kab_kota'] = 'N/A'
                            list_item['kab_kota'] = row[0] 
                            list_item['kecamatan'] = 'N/A'
                            list_item['populasi'] = 'N/A'
                            list_item['lat_kab_kota'] = 'N/A'
                            list_item['long_kab_kota'] = 'N/A'
                            list_item['n_odr'] = 'N/A'
                            list_item['n_otg'] = int(str(row[1]).rstrip())
                            list_item['n_odp'] = int(str(row[3]).rstrip())
                            list_item['n_pdp'] = int(str(row[4]).rstrip())
                            list_item['n_confirm'] = int(str(row[2]).rstrip())
                            list_item['n_meninggal'] = 'N/A'
                            list_item['n_sembuh'] = 'N/A'
                            list_item['last_update'] = _last_update
                            #print(list_item)
                            kabkota = KabupatenKota.select().where(KabupatenKota.prov_id==propinsi, 
                                KabupatenKota.nama==row[0])

                            if kabkota.count() < 1:
                                kabkota =KabupatenKota.create(prov_id=propinsi, 
                                    nama=row[0])
                            else:
                                kabkota  = kabkota.get()

                            datum = Data.select().where(Data.kabupaten==kabkota, Data.last_update==dateparser.parse(_last_update))
                            if datum.count() < 1:
                                datum = Data.create(
                                    kabupaten=kabkota,
                                    n_otg=int(str(row[1]).rstrip()),
                                    n_odp=int(str(row[3]).rstrip()),
                                    n_pdp=int(str(row[4]).rstrip()),
                                    n_confirm=int(str(row[2]).rstrip()),
                                    last_update=dateparser.parse(_last_update)
                                )
                            output['result'].append(list_item)

                        i=i+1

            return output

        elif prov=='bali':
            propinsi = Province.select().where(Province.nama_prov=='Bali')
            if propinsi.count() < 1:
                propinsi =Province.create(nama_prov='Bali', alias=prov)
            else:
                propinsi  = propinsi.get()
            sekarang = datetime.datetime.now().date()
            try:
                result = list(Data.select().join(Province).where(fn.date_trunc('day', Data.last_update) == sekarang), Province.alias==prov)
            except:
                result = []
            if len(result) > 0:
                return result
            link = 'https://pendataan.baliprov.go.id/'
            output = {}
            output['result'] = []  
            with requests.session() as s:

                r = s.get(link,verify=True)
                data = r.text
                url = soup(data,"lxml")

                con = url.find_all('div', attrs={'card-header'})
                title = con[6].find('h3').text
                pos = str(title).rfind('Dengan ')
                _last_update = str(title)[pos+7:]

                table = url.find('table', attrs={'class':'table'})
                #print(table)

                if table is not None:
                    res = []
                    table_rows = table.find_all('tr')
                    num_rows = len(table_rows)

                    i = 0
                    for tr in table_rows:
                        td = tr.find_all('td')
                        row = [tr.text.strip() for tr in td if tr.text.strip()]
                        #print(row)
                        if i>=1 and i<num_rows-1:
                            if row:
                                list_item = {}
                                list_item['provinsi'] = 'Bali'
                                list_item['kode_kab_kota'] = 'N/A'
                                list_item['kab_kota'] = row[0] 
                                list_item['kecamatan'] = 'N/A'
                                list_item['populasi'] = 'N/A'
                                list_item['lat_kab_kota'] = 'N/A'
                                list_item['long_kab_kota'] = 'N/A'
                                list_item['n_odr'] = 'N/A'
                                list_item['n_otg'] = 'N/A'
                                list_item['n_odp'] = 'N/A'
                                list_item['n_pdp'] = int(str(row[7]).rstrip())
                                list_item['n_confirm'] = int(str(row[6]).rstrip())
                                list_item['n_meninggal'] = int(str(row[9]).rstrip())
                                list_item['n_sembuh'] = int(str(row[8]).rstrip())
                                list_item['last_update'] = _last_update
                                #print(list_item)
                                kabkota = KabupatenKota.select().where(KabupatenKota.prov_id==propinsi, 
                                    KabupatenKota.nama==row[0])

                                if kabkota.count() < 1:
                                    kabkota =KabupatenKota.create(prov_id=propinsi, 
                                        nama=row[0])
                                else:
                                    kabkota  = kabkota.get()

                                datum = Data.select().where(Data.kabupaten==kabkota, Data.last_update==dateparser.parse(_last_update))
                                if datum.count() < 1:
                                    datum = Data.create(
                                        kabupaten=kabkota,
                                        n_pdp=int(str(row[7]).rstrip()),
                                        n_confirm=int(str(row[6]).rstrip()),
                                        n_meninggal=int(str(row[9]).rstrip()),
                                        n_sembuh=int(str(row[8]).rstrip()),
                                        last_update=dateparser.parse(_last_update)
                                    )
                                output['result'].append(list_item)
                        i=i+1
            return output
        
        elif prov=='banten':
            propinsi = Province.select().where(Province.nama_prov=='Banten')
            if propinsi.count() < 1:
                propinsi =Province.create(nama_prov='Banten', alias=prov)
            else:
                propinsi  = propinsi.get()
            sekarang = datetime.datetime.now().date()
            try:
                result = list(Data.select().join(Province).where(fn.date_trunc('day', Data.last_update) == sekarang), Province.alias==prov)
            except:
                result = []
            if len(result) > 0:
                return result
            link = 'https://infocorona.bantenprov.go.id/'
            output = {}
            output['result'] = []        
            with requests.session() as s:
                r = s.get(link,verify=True)
                data = r.text
                url = soup(data,"lxml")

                script = url.find_all('script')
                json_data = ''
                for item in script:
                    if re.search(r'pieSeries.data\s\=\s(.*)\;',str(item)):
                        var_data = re.findall(r'pieSeries.data\s\=\s(.*)\;',str(item))
                        json_data = json.loads(str(var_data[0]))


                for data in json_data:
                    list_item = {}
                    list_item['provinsi'] = 'Banten'                
                    list_item['kode_kab_kota'] = 'N/A'
                    list_item['kab_kota'] = data['title']
                    list_item['kecamatan'] = 'N/A'
                    list_item['populasi'] = 'N/A'
                    list_item['lat_kab_kota'] = data['latitude']
                    list_item['long_kab_kota'] = data['longitude']              
                    list_item['n_odr'] = 'N/A'
                    list_item['n_otg'] = 'N/A'
                    list_item['n_odp'] = data['pieData'][0]['value']
                    list_item['n_pdp'] = data['pieData'][1]['value']
                    list_item['n_confirm'] = data['pieData'][2]['value']
                    list_item['n_meninggal'] = 'N/A'
                    list_item['n_sembuh'] = 'N/A'
                    list_item['last_update'] = 'N/A'

                    kabkota = KabupatenKota.select().where(KabupatenKota.prov_id==propinsi, 
                        KabupatenKota.nama==data['title'])

                    if kabkota.count() < 1:
                        kabkota =KabupatenKota.create(prov_id=propinsi, 
                            nama=data['title']
                            lat=data['latitude'], lon=data['longitude'],populasi='')
                    else:
                        kabkota  = kabkota.get()

                    datum = Data.select().where(Data.kabupaten==kabkota, Data.last_update==datetime.datetime.now())
                    if datum.count() < 1:
                        datum = Data.create(
                            kabupaten=kabkota,
                            n_odp=data['pieData'][0]['value'],
                            n_pdp=data['pieData'][1]['value'],
                            n_confirm=data['pieData'][2]['value'],
                            last_update=datetime.datetime.now()
                        )

                    output['result'].append(list_item)

            return output 
        elif prov=='sulbar':
            propinsi = Province.select().where(Province.nama_prov=='Sulawesi Barat')
            if propinsi.count() < 1:
                propinsi =Province.create(nama_prov='Sulawesi Barat', alias=prov)
            else:
                propinsi  = propinsi.get()
            sekarang = datetime.datetime.now().date()
            try:
                result = list(Data.select().join(Province).where(fn.date_trunc('day', Data.last_update) == sekarang), Province.alias==prov)
            except:
                result = []
            if len(result) > 0:
                return result
            link = 'https://covid19.sulbarprov.go.id/utama/data'
            output = {}
            output['result'] = []  
            with requests.session() as s:

                r = s.get(link,verify=True)
                data = r.text
                url = soup(data,"lxml")

                table = url.find('table', attrs={'class':'table-responsive'})
                #print(table)

                if table is not None:
                    res = []
                    table_rows = table.find_all('tr')
                    num_rows = len(table_rows)

                    i = 0
                    for tr in table_rows:
                        td = tr.find_all('td')
                        row = [tr.text.strip() for tr in td if tr.text.strip()]
                        #print(row)
                        if i>=1 and i<num_rows-1:
                            if row:
                                list_item = {}
                                list_item['provinsi'] = 'Sulawesi Barat'
                                list_item['kode_kab_kota'] = 'N/A'
                                list_item['kab_kota'] = str(row[1]).rstrip()
                                list_item['kecamatan'] = 'N/A'
                                list_item['populasi'] = 'N/A'
                                list_item['lat_kab_kota'] = 'N/A'
                                list_item['long_kab_kota'] = 'N/A'
                                list_item['n_odr'] = 'N/A'
                                list_item['n_otg'] = int(str(row[6]).rstrip())
                                list_item['n_odp'] = int(str(row[2]).rstrip())
                                list_item['n_pdp'] = int(str(row[10]).rstrip())
                                list_item['n_confirm'] = int(str(row[14]).rstrip())
                                list_item['n_meninggal'] = int(str(row[5]).rstrip()) + int(str(row[9]).rstrip()) + int(str(row[12]).rstrip()) + int(str(row[18]).rstrip())
                                list_item['n_sembuh'] = int(str(row[17]).rstrip())
                                list_item['last_update'] = 'N/A'
                                #print(list_item)
                                kabkota = KabupatenKota.select().where(KabupatenKota.prov_id==propinsi, 
                                    KabupatenKota.nama==row[1])

                                if kabkota.count() < 1:
                                    kabkota =KabupatenKota.create(prov_id=propinsi, 
                                        nama=row[1])
                                else:
                                    kabkota  = kabkota.get()

                                datum = Data.select().where(Data.kabupaten==kabkota, Data.last_update==datetime.datetime.now())
                                if datum.count() < 1:
                                    datum = Data.create(
                                        kabupaten=kabkota,
                                        n_otg=int(str(row[6]).rstrip()),
                                        n_odp=int(str(row[2]).rstrip()),
                                        n_pdp=int(str(row[10]).rstrip()),
                                        n_confirm=int(str(row[14]).rstrip()),
                                        n_meninggal=int(str(row[5]).rstrip()) + int(str(row[9]).rstrip()) + int(str(row[12]).rstrip()) + int(str(row[18]).rstrip()),
                                        n_sembuh=int(str(row[17]).rstrip()),
                                        last_update=datetime.datetime.now()
                                    )
                                output['result'].append(list_item)
                        i=i+1
            return output
        

