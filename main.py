#    IMPORTS    #

import os, time

import xml.etree.ElementTree as ET

import requests

from datetime import date, datetime, timedelta

import datetime

import csv

import numpy as np

import nltk

from nltk.sentiment import SentimentIntensityAnalyzer

from prettytable import PrettyTable

from prettytable import MSWORD_FRIENDLY

from itertools import count




#   Variables GLobales    #

headlines = {'source': [], 'title': [], 'pubDate' : [], 'count' : [] }
categorised_headlines = {}
sentiment = {}
compiled_sentiment = {}
headlines_analysed = {}

titulos_Cargados = False
archivo_CSV = 'Crypto feeds.csv'
feeds = []

keywords = {
    'XRP': ['ripple', 'xrp', 'XRP', 'Ripple', 'RIPPLE'],
    'BTC': ['BTC', 'bitcoin', 'Bitcoin', 'BITCOIN'],
    'XLM': ['Stellar Lumens', 'XLM'],
    'BCH': ['Bitcoin Cash', 'BCH'],
    'ETH': ['ETH', 'Ethereum'],
    'BNB' : ['BNB', 'Binance Coin'],
    'LTC': ['LTC', 'Litecoin'],
    'DOGE': ['DOGE', 'Dogecoin'],

    }



#    CARGAR CSV    #
with open(archivo_CSV) as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader, None)
    for row in csv_reader:
        feeds.append(row[0])

#Extraer titulares del xml
def get_headlines():                                                            #GET HEADLINES --------------------
    global headlines
    start = time.time()
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0'
    }
    for feed in feeds:
        try:
            count = 0
            r = requests.get(feed, headers=headers, timeout=7)
            root = ET.fromstring(r.text)
            for i in root.iter('item'):
                count = count + 1
                pubDate = i.find('pubDate').text
                titulo = i.find('title').text
                headlines['source'].append(feed)
                headlines['title'].append(titulo)
                headlines['pubDate'].append(pubDate)
                headlines['count'].append(count)
                print(titulo)
        except:
            print(f'No se puede leer {feed}')
    end = time.time()
    print ('\n Ha transcurrido ' + str(end - start) + ' segundos')
    print('')
    print('Se han capturado ' + str(len(headlines['title'])) + ' titulares')
    global titulos_Cargados
    titulos_Cargados = True
    categorise_headlines()


#Añadir titular a cada indice
def categorise_headlines():                                                     #CATEGORIZE HEADLINES --------------------
    global categorised_headlines
    for keyword in keywords:
        categorised_headlines['{0}'.format(keyword)] = []
    for keyword in keywords:
        for headline in headlines['title']:
            if any(key in headline for key in keywords[keyword]):
                categorised_headlines[keyword].append(headline)
    analyse_headlines()


#Analisis de tiutlares con SentimentIntensityAnalyzer
def analyse_headlines():                                                        #ANALYZE HEADLINES --------------------
    global sentiment
    sia = SentimentIntensityAnalyzer()
    for coin in categorised_headlines:
        if len(categorised_headlines[coin]) > 0:
            sentiment['{0}'.format(coin)] = []
            for title in categorised_headlines[coin]:
                sentiment[coin].append(sia.polarity_scores(title))
    compile_sentiment()

#Recoger valor compound
def compile_sentiment():                                                        #COMPILE SENTIMENT --------------------
    global compiled_sentiment
    for coin in sentiment:
        compiled_sentiment[coin] = []
        for item in sentiment[coin]:
            compiled_sentiment[coin].append(sentiment[coin][sentiment[coin].index(item)]['compound'])
    compound_average()



#Media
def compound_average():                                                         #COMPOUND AVERAGE
    global compiled_sentiment
    global headlines_analysed
    for coin in compiled_sentiment:
        headlines_analysed[coin] = len(compiled_sentiment[coin])
        # calculate the average using numpy if there is more than 1 element in list
        compiled_sentiment[coin] = np.array(compiled_sentiment[coin])
        # get the mean
        compiled_sentiment[coin] = np.mean(compiled_sentiment[coin])
        # convert to scalar
        compiled_sentiment[coin] = compiled_sentiment[coin].item()


def analisis():                                                                      #ANALISIS
    get_headlines()

    menu('fin-inicio')

#borrar consola
def cls():
    os.system('cls' if os.name=='nt' else 'clear')



def selector(opcion,tipo):
    global headlines_analysed
    global compile_sentiment
    global keywords
    global titulos_Cargados #interruptor inidica si se ha iniciado la busqueda de titulos
    global headlines

    if tipo == 'menu-principal':
        if opcion == '1' and titulos_Cargados == True:                          #CUANDO SE VUELVE A INICIAR EL PROGRAMA POR 2º VEZ
            interruptor = False

            while interruptor == False:
                print('Ya hay titulos cargados ¿quieres sobreescribirlos?')
                print('1. Si')
                print('2. No')
                inputSobreescribir = input()
                if inputSobreescribir == '1':
                    interruptor = True
                    headlines_analysed.clear()
                    compiled_sentiment.clear()
                    headlines.clear()
                    headlines = {'source': [], 'title': [], 'pubDate' : [], 'count' : [] }
                    analisis()
                elif inputSobreescribir == '2':
                    interruptor = True
                    menu('menu-principal')
                else:
                    print('Opcion incorrecta')

        if opcion == '1':#CUANDO SE INICIA EL PROGRAMA POR 1ºVEZ
            analisis()


        elif opcion == '2':                                                     #iMPORTAR ARCHIVO CSV

            global feeds
            global archivo_CSV
            print('Introduce el nombre de tu archivo CSV (Debe de estar en la carpeta raiz , por defecto Crypto feeds.csv )')
            print('Introduce "x" si quieres volver al menu')
            print('')
            input_Archivo = input()

            if input_Archivo == 'x':
                menu('menu-principal')

            else:
                archivo_CSV = input_Archivo
                feeds.clear()

                with open(archivo_CSV) as csv_file:

                    # open the file
                    csv_reader = csv.reader(csv_file)

                    # remove any headers
                    next(csv_reader, None)

                    # add each row cotaining RSS url to feeds list
                    for row in csv_reader:
                        feeds.append(row[0])

                print("Tu archivo se ha cargado correctamente")
                time.sleep(2)

            menu('menu-principal')

        elif opcion == '3':                                                     #CRIPTOS Y TAGS
            interruptor_General= False
            interruptor = False
            interruptor2 = False

            while interruptor_General == False: #While menu general

                menu('menu-crip')
                input_Gen = input()

                if input_Gen == '1':#Mostrar criptos
                    cls()

                    Z =  PrettyTable()
                    #Z.set_style(MSWORD_FRIENDLY)
                    Z.field_names = ['Indice' , 'Tags']
                    for x in keywords:
                        tagss = str(keywords[x])
                        tagss = tagss.replace('[' , "")
                        tagss = tagss.replace(']' , "")
                        tagss = tagss.replace("'" , "")
                        Z.add_row([x , tagss])

                    print(Z)
                    print("")
                    print("")
                    print("1. Volver atras")
                    input_atras = input()

                    while input_atras != '1':#While volver atras
                        print("Opcion incorrecta")
                        print("1. Volver atras")
                        input_atras = input()



                elif input_Gen == '2':#Añadir criptos

                    interruptor_General= True
                    interruptor = False
                    interruptor2 = False

                    while interruptor == False:

                        print('')
                        print("Añade el nombre de tu indice")
                        input_moneda = input()

                        keywords[input_moneda] = []

                        while interruptor2 == False:

                            print("Añade un tag, introduce 'x' para finalizar")
                            input_tag = input()
                            if input_tag == 'x':
                                interruptor2 = True
                            else:
                                keywords[input_moneda].append(input_tag)


                        print('')
                        print('1. Añadir otro')
                        print('2. Atras')
                        input_opcion = input()

                        if input_opcion == '2':
                            interruptor2= True
                            interruptor= True
                            interruptor_General = False

                        elif input_opcion == '1':
                            print('Añade otra')
                            interruptor2=False


                        else:
                            print('Opcion incorrecta')


                elif input_Gen == '3':

                    print('Que moneda quieres eliminar?')
                    print('')
                    for x in keywords:
                        print(x)

                    input_del = input()

                    keywords.pop(input_del,None)

                    print('Se ha eliminado ' + input_del)

                    time.sleep(2)
                    menu('menu-crip')

                elif input_Gen == '4':
                    interruptor_General = True
                    menu('menu-principal')


                else:
                    print("Opcion incorrecta")
                    time.sleep(2)





        elif opcion == '4':
            sia = SentimentIntensityAnalyzer()

            interruptor_op4 = False

            while interruptor_op4 == False:
                cls()
                interruptor_op44 = False
                print('Introduce tu frase, debe estar en ingles, introduce X para salir')
                frase = input()
                if frase == 'x':
                    menu('menu-principal')
                else:
                    print(sia.polarity_scores(frase))

                    while interruptor_op44 == False:
                        print("")
                        print("1. Introducir otra frase")
                        print("2. Volver atras")
                        opcion = input()
                        if opcion == '2':
                            interruptor_op4 = True
                            interruptor_op44 = True
                            menu('menu-principal')

                        elif opcion != '1':
                            print('opcion incorrecta')

                        else:
                            interruptor_op44 = True



        elif opcion == '5':
                                                    #EXPORTAR INFORMACIO
            now = datetime.datetime.now()
            fecha = str(now.hour)+ 'h-' + str(now.minute)+ 'm-' + str(now.second) + 's'

            fileOpen = open("data" + fecha + ".csv", "w")
            writer = csv.writer(fileOpen)
            for key , val in compiled_sentiment.items():
                writer.writerow([key , val])

            fileOpen.close()
            print("Se ha exportado correctamente")
            time.sleep(2)
            menu('menu-principal')

        else:
            print('Opcion incorrecta')
            time.sleep(2)
            cls()
            menu('menu-principal')

    elif tipo == 'fin-inicio':
        if opcion == '1':
            for coin in compiled_sentiment:
                print("")
                print(f'{coin} sentimiento: {compiled_sentiment[coin]} --- Titulos analizados: {headlines_analysed[coin]}')
            menu('fin-inicio-mostrar')

        elif opcion == '2':
            menu('menu-principal')
        else:
            print('Opcion incorrecta')
            time.sleep(2)
            cls()
            menu('fin-inicio')

    elif tipo == 'fin-inicio-mostrar':
        if opcion == '1':
            menu('menu-principal')
        else:
            print('Opcion incorrecta')
            time.sleep(2)
            cls()
            menu('fin-inicio-mostrar')

def menu(tipo):
#-------------------
#Menu-principal
#fin-inicio
#fin-inicio-mostrar
#-------------------

#MENU PRINCIPAL
    if tipo == 'menu-principal':
        cls()
        print('                    ----NLTK ANALYZER----                       ')
        print('')
        print('Analizador de sentimientos en titulares respecto a criptomonedas')
        print('')
        print('1. Iniciar')
        print('2. Importar CSV')
        print('3. Añadir indices')
        print('4. Probar analizador nltk')
        print('5. Exportar datos')
        print('6. Configuracion')
        print('')
        opcion = input()
        selector(opcion, 'menu-principal')

#MENU AL FINALIZAR ANALISIS
    elif tipo == 'fin-inicio':
        print('')
        print('1. Mostrar informacion')
        print('2. Volver al menu')
        opcion = input()
        selector(opcion, 'fin-inicio')

#MENU AL FINALIZAR ANALISIS MOSTRANDO DATOS
    elif tipo == 'fin-inicio-mostrar':
        print('')
        print('1. Volver al menu')
        opcion = input()
        selector(opcion, 'fin-inicio-mostrar')


    elif tipo == 'menu-crip':
        cls()
        print("1. Mostrar indices y tags")
        print("2. Añadir indice")
        print("3. Eliminar indice")
        print('4. Atras')


if __name__ == '__main__':                                                      # MAIN --------------------



    menu('menu-principal')
