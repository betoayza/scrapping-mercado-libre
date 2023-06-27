from bs4 import BeautifulSoup
import requests
from termcolor import colored
import pandas
import re


def format_data(log):
    pattern = r"\bAhora\b.*?\bpesos\b"
    pattern_2 = r"\.\d{3}"
    pattern_3 = r"\$"
    pattern_4 = r"^\S+"
    pattern_5 = r"%\s\d+\s"
    pattern_6 = r"^Mismo\sprecio\sen\s\d+\scuotas\sde\s+\d+\.\d+$"
    pattern_7 = r"^\d+%$"
    pattern_8 = r"^\d+\.\d+$"

    log = log.replace("OFERTA DEL DÍA", "")
    log = log.replace("cuotas de $ ", "cuotas de ")
    log = log.replace("Llega gratis", " Llega gratis")
    log = log.replace("OFFAntes: ", "")
    log = log.replace("pesos", "")
    log = log.replace("Ahora: ", "")
    log = log.replace(",", "")
    log = re.sub(pattern, "", log)
    log = re.sub(pattern_2, lambda match: match.group() + " ", log)
    log = re.sub(pattern_3, "", log)
    log = re.sub(pattern_4, "", log)
    log = log.replace(" Llega gratis", ",Llega gratis")
    log = log.replace("Mismo precio", ",Mismo precio")
    log = re.sub(pattern_5, "%,", log)
    log = log[1:]
    log = re.sub(pattern_2, lambda match: match.group() + ",", log)
    log = log.replace(", ", ",")

    log = log.split(",")

    if log[-1] != "Llega gratis mañana":
        log.append("Sin datos")

    log = [x for x in log if x != ""]

    if not re.search(pattern_7, log[1]):
        log.insert(1, "Sin datos")

    if not re.search(pattern_8, log[2]):
        log.insert(2, "Sin datos")

    if not re.search(pattern_6, log[3]):
        log.insert(3, "Sin datos")

    return log


def add_to_data(log):
    data.append(log)


url = "https://www.mercadolibre.com.ar/ofertas#c_id=/home/promotions-recommendations/element&c_uid=00fbf8a7-12d7-4f0a-a8a7-a047948a61fe"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
pretty_soup = soup.prettify()
items_list = soup.find("ol", {"class": "items_container"})
data = []


for item in items_list:
    item_text = item.get_text()
    log = format_data(item_text)

    add_to_data(log)


try:
    df = pandas.DataFrame(
        data,
        columns=[
            "OFERTA",
            "DESCUENTO",
            "PRECIO ORIGINAL",
            "CUOTAS",
            "PRODUCTO",
            "ENVIO",
        ],
    )

    df.to_csv("output.csv", index=False)

    print("CSV file created!")
except Exception as error:
    print(colored(f"\n\nError: {error}", "red"))
