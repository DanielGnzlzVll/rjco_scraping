'''Modulo para web scraping de la pagina de la Rama judicial Colombiana,
encuentra demandas encontra de las personas juridicas.
===================
import rjco_scraping
results = rjco_scraping.scraping(text2search="sura", output_file="result.xlsx")
'''
from .scraping import scraping