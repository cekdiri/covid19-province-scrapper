import importlib


class Scrapper:

    def get_pos(str_lf,str_rg,text):
        left = text.find(str_lf)
        right = text.rfind(str_rg)

        return left, right

    def scrapper(prov):
        scrapper = importlib.import_module('scrappers.{}'.format(prov))
        return scrapper.scrape()


