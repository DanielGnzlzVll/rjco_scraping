import glob
import logging
import os
import sys
import time
import urllib

import click
import coloredlogs
import pandas as pd
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)
coloredlogs.install(
    level=getattr(logging, os.getenv("logLevel", "info").upper()),
    logger=logger,
    fmt="[%(levelname)s] - %(asctime)s - %(processName)s|%(funcName)s(%(lineno)s): %(message)s",
)
logger.debug("Iniciando app")
# Constantes
ENTRY_ENDPOINT = (
    r"https://procesos.ramajudicial.gov.co/consultaprocesos/ConsultaJusticias21.aspx"
)


def remove_temp_files():
    files = glob.glob("*.csv")
    for file in files:
        try:
            os.remove(file)
        except Exception as e:
            logger.error("No se ha podido eliminar el archivo temporal: " + file)
            logger.exception(e)


def wait_for_by_name(driver, element_name, timeout=10):
    """Espera a que un elemento con el nombre =  element_name
    este presente, y lo devuelve.
    
    :param driver: driver a usar
    :type driver: webdriver.WebDriver
    :param element_name: atributo html ´´name´´ del elemento a buscar
    :type element_name: str
    :return: elemento buscado
    :rtype: webelement.WebElement
    """

    wait = WebDriverWait(driver, timeout)
    logger.debug("Esperando por: " + element_name)
    element = wait.until(ec.visibility_of_element_located((By.NAME, 
                                                            element_name)))
    logger.debug(element_name + ": OK")
    return element


def wait_for_by_xpath(driver, element_xpath, timeout=10, wait_visibility=True):
    """Espera a que un elemento con la ruta =  element_xpath
    este presente, y lo devuelve.
    
    :param driver: driver a usar
    :type driver: webdriver.WebDriver
    :param element_xpath: expresion xpath dentro del html del driver
    :type element_xpath: str
    :param timeout: tiempo maximo a esperear
    :type timeout: float
    :param wait_visibility: esperara a que este visible o invisible
    :type wait_visibility: bool
    :return: elemento buscado
    :rtype: webelement.WebElement
    """

    wait = WebDriverWait(driver, timeout)
    logger.debug("Esperando por: " + element_xpath)
    if wait_visibility:
        check = ec.visibility_of_element_located
    else:
        check = ec.invisibility_of_element_located
    element = wait.until(check((By.XPATH, element_xpath)))
    logger.debug(element_xpath + ": OK")
    return element


def wait_for_all_by_name(driver, element_name, timeout=10):
    """Espera a que un elemento con el nombre =  element_name
    este presente, y lo devuelve.
    
    :param driver: driver a usar
    :type driver: webdriver.WebDriver
    :param element_name: atributo html ´´name´´ del elemento a buscar
    :type element_name: str
    :return: elemento buscado
    :rtype: webelement.WebElement
    """

    wait = WebDriverWait(driver, timeout)
    logger.debug("Esperando por: " + element_name)
    element = wait.until(ec.visibility_of_all_elements_located((By.NAME,
                                                                element_name)))
    logger.debug(element_name + ": OK")
    return element


def get_options(driver, element_name):
    element = wait_for_by_name(driver, element_name)
    select_element = Select(element)
    elements = {
        element.text: element.get_attribute("value")
        for element in select_element.options[1:]
    }
    return elements


def handle_error(driver):
    """Busca el boton de ´´Cerrar´´ y lo presiona
    
    :param driver: driver a usar
    :type driver: webdriver.WebDriver
    """

    logger.debug("Presionando boton cerrar")
    xpath = "//div[@id='modalError']//*/td/input[@value='Cerrar' and @type='button']"
    element_error_button = driver.find_element_by_xpath(xpath)
    element_error_button.click()
    logger.debug("Presionando boton cerrar: ok")


def test_error(driver):
    """Checkea si esta desplegada la ventana de error y lo maneja
    
    :param driver: driver a usar
    :type driver: webdriver.WebDriver
    :return: True si hay error, y False en caso contrario
    :rtype: bool
    """

    try:
        wait = WebDriverWait(driver, 3)
        xpath = "//div[@id='modalError' and @style='display: block;']"
        element_error = wait.until(ec.visibility_of_element_located((By.XPATH,
                                                                    xpath)))
        handle_error(driver)
        return True
    except TimeoutException as e:
        return False


def scrap_entity(driver, entity_name, entity_code, text2search):
    logger.info("Obteniendo datos para: " + entity_name.strip())
    df = pd.DataFrame()
    # Se selecciona la entidad
    ddlEntidadEspecialidad = wait_for_by_name(driver, "ddlEntidadEspecialidad")
    select_entidad = Select(ddlEntidadEspecialidad)
    select_entidad.select_by_value(entity_code)
    if test_error(driver):
        logger.error(
            "Se ha presentado una ventana "
            "de error inexperada para la entidad: " + entity_name.strip()
        )
        return df
    rblConsulta = wait_for_by_name(driver, "rblConsulta")
    select_person = Select(rblConsulta)
    select_person.select_by_index(1)
    ddlTipoSujeto = wait_for_by_name(driver, "ddlTipoSujeto")
    select_subject_type = Select(ddlTipoSujeto)
    select_subject_type.select_by_index(2)

    ddlTipoPersona = wait_for_by_name(driver, "ddlTipoPersona")
    select_person_type = Select(ddlTipoPersona)
    select_person_type.select_by_index(2)

    txtNatural = wait_for_by_name(driver, "txtNatural")
    txtNatural.clear()
    txtNatural.send_keys(text2search)

    # slider
    sliderBehaviorConsultaNom_railElement = driver.find_element_by_id(
        "sliderBehaviorConsultaNom_railElement"
    )
    move = ActionChains(driver)
    move.click_and_hold(sliderBehaviorConsultaNom_railElement).move_by_offset(
        10, 0
    ).release().perform()

    btnConsultaNom = wait_for_by_name(driver, "btnConsultaNom")
    btnConsultaNom.click()
    try:
        time.sleep(1)
        ## esperar a que el boton de ´´Cargando´´ cambie su estilo a displat: none
        xpath = "//div[@id='miVentana']"
        wait_for_by_xpath(driver, xpath, timeout=30, wait_visibility=False)
    except TimeoutException:
        logger.info("No lo encuentro")
    if test_error(driver):
        logger.error(
            "Se ha presentado una ventana "
            "de error inexperada para la entidad: " + entity_name.strip()
        )
        return df

    # esperar resultados
    btnGetCSV = wait_for_by_name(driver, "btnGetCSV")
    btnGetCSV.click()
    # los resultados son presentados para descargar mediante un link
    # se obtiene el link y se descarga directamente.
    xpath_rsult = "//div[@id='updResultadosNum']/span[@id='lblCSVFileStatus']/b/a"
    url_link = wait_for_by_xpath(driver, xpath_rsult).get_attribute("href")
    url_link = url_link.replace("')", "")
    url_link = url_link.replace("javascript:abrirDocumento('", "")
    filename = url_link.split("/")[-1]
    urllib.request.urlretrieve(url_link, filename=filename)

    df = pd.read_csv(
        filename, encoding="utf-16", sep=";", skiprows=[0], usecols=range(6)
    )
    df["Entidad"] = entity_name
    logger.info(entity_name.strip() + ": OK")
    return df


def scrap_city(driver, city_name, city_code, text2search):
    logger.info("*****Obteniendo datos para: " + city_name.strip())
    df = pd.DataFrame()
    # Se selecciona la ciudad
    ddlCiudad = wait_for_by_name(driver, "ddlCiudad")
    select_city = Select(ddlCiudad)
    select_city.select_by_value(city_code)
    if test_error(driver):
        logger.error(
            "Se ha presentado una ventana "
            "de error inexperada para la ciudad: " + city_name.strip()
        )
        return df
    # Se obtiene la lista de entidades desde el selector
    entitys = get_options(driver, "ddlEntidadEspecialidad")
    for entity in entitys:
        try:
            if not "(Inactivo)" in entity:
                # Cuando la entidad no esta disponible, se añade "(Inactivo)"
                # al nombre de la misma
                df_temp = scrap_entity(driver, entity, entitys[entity], text2search)
                df = pd.concat([df, df_temp], sort=True)
            else:
                continue
        except Exception as e:
            logger.error(
                "=====>Error al obtener datos de la entidad: " + entity.strip()
            )
            logger.exception(e)

    df["Ciudad"] = city_name
    logger.info(city_name.strip() + ": OK*****")
    return df


def scraping(text2search="sura", output_file="result.xlsx"):
    """Esta funcion permite buscar en la url ´´ENTRY_ENDPOINT´´
    de la Rama judicial Colombiana los procesos de demanda encontra
    de personas juridicas cuya razon coincida con ´´text2search´´ y
    almacenar los resultados en un archivo de excel.
    
    :param text2search: Parametros de busqueda, defaults to "sura"
    :type text2search: str, optional
    :param output_file: , defaults to "result.xlsx"
    :type output_file: str, optional
    :return: resultados en cada entidad registrada en dicha pagina
    :rtype: pf.DataFrame
    """

    logger.info("Iniciando scraping")
    df = pd.DataFrame()
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(ENTRY_ENDPOINT)
        if test_error(driver):
            logger.error("Se ha presentado una ventana de error inexperada")
            return df
        # Se obtiene la lista de ciudad desde el selector
        citys = get_options(driver, "ddlCiudad")
        for city in citys:
            try:
                df_temp = scrap_city(driver, city, citys[city], text2search)
                df = pd.concat([df, df_temp], sort=True)
            except Exception as e:
                logger.error(
                    "=====>Error al obtener datos de la ciudad: " + city.strip()
                )
                logger.exception(e)
    except RequestException as e:
        logger.error("Parece que algo esta mal con la conexion a internet")
    except KeyboardInterrupt:
        logger.warning("Programa detenido")
    except Exception as e:
        logger.error("Un error inexperado ha ocurrido")
        logger.exception(e)
    finally:
        try:
            driver.close()
        except:
            pass
        remove_temp_files()
        try:
            df.to_excel("result.xlsx")
        except Exception as e:
            logger.error("No se ha podido guardar el resultado")
            logger.exception(e)

    logger.info("Scraping terminado")


@click.command()
@click.option(
    "--text2search",
    prompt="Ingrese el texto a durante la busqueda",
    help="Texto a buscar",
)
@click.option("--output_file", default="output.xlsx")
def scraping_wraper(text2search, output_file):
    return scraping(text2search, output_file)


if __name__ == "__main__":
    scraping_wraper()
