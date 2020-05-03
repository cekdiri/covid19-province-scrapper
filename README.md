COVID-19 Scraper
===
Script ini mengumpulkan data OTG, ODP, PDP, Pasien Positif, Pasien Meninggal dan Pasien Sembuh dari provinsi-provinsi di seluruh Indonesia.

Dua fungsi utamanya adalah sebagai scrapper sekaligus juga sebagai server API.

Requirements
---
- Python 3
- selenium
- chromedriver/geckodriver
- python-requests
- Flask
- Peewee
- MySQL

Installation
---
- `https://github.com/cekdiri/covid19-province-scrapper.git`
- `cd covid19-province-scrapper`
- Jika belum punya pipenv, jalankan `pip install pipenv`
- Jalankan `pipenv install`

Usage
---
```
Isikan user mysql, password dan nama database di settings.cfg

Jalankan: 
python app.py 

akses melalui browser: 
http://localhost:5000/api/<kodeprovinsi>

contoh:

http://localhost:5000/api/aceh
```

Contributor
---
- [Sigit Poernomo](https://github.com/sigit-purnomo)
- [Rony Lantip](https://github.com/lantip)

Table Kode Provinsi
---

| Nama Provinsi      | Kode   |
|--------------------|--------|
| D.I. Aceh          | aceh   |
| Jawa Timur         | jatim  |
| Kalimantan Selatan | kalsel |
| Sumatera Utara     | sumut  |
| D.I. Yogyakarta    | diy    |
| Sulawesi Selatan   | sulsel |
| Bangka Belitung    | babel  |
| Bali               | bali   |
| Sulawesi Barat     | sulbar |
| Banten             | banten |