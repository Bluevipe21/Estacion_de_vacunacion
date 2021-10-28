import nltk
from nltk.stem.lancaster import LancasterStemmer

stemmer=LancasterStemmer()
import numpy
import tflearn
import tensorflow
import json
import random
import pickle
import pyttsx3
import speech_recognition as sr 
import datetime
from datetime import date
import time
import cv2
import sqlite3
import datetime
from xlsxwriter.workbook import Workbook 
import pytesseract 
import re

#nltk.download('punkt')
######Para la base de datos#######
vacunaIndividual=""
dosisIndividual=""
##################################
r=sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')

engine.setProperty('voice', voices[0].id) #Voz de Helena local de windows
engine.setProperty('rate',145)

#Variables para obtener fecha por voz 
MONTHS=["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]
DAYS=["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]
#####################################

with open("intents.json",encoding='utf-8') as archivo:
	datos=json.load(archivo)

palabras=[]
tags=[]
auxX=[]
auxY=[]

for contenido in datos["contenido"]:
	for patrones in contenido["patrones"]:
		auxPalabra=nltk.word_tokenize(patrones)
		palabras.extend(auxPalabra)
		auxX.append(auxPalabra)
		auxY.append(contenido["tag"])

		if contenido["tag"] not in tags:
			tags.append(contenido["tag"])

palabras=[stemmer.stem(w.lower()) for w in palabras if w!="?"]
palabras=sorted(list(set(palabras)))
tags=sorted(tags)

entrenamiento=[]
salida=[]
salidaVacia=[0 for _ in range(len(tags))]

for x,documento in enumerate(auxX):
	cubeta=[]
	auxPalabra=[stemmer.stem(w.lower()) for w in documento]
	for w in palabras:
		if w in auxPalabra:
			cubeta.append(1)
		else:
			cubeta.append(0)
	filaSalida=salidaVacia[:]
	filaSalida[tags.index(auxY[x])]=1
	entrenamiento.append(cubeta)
	salida.append(filaSalida)


#print(entrenamiento)
#print(salida)

entrenamiento=numpy.array(entrenamiento)
salida=numpy.array(salida)

tensorflow.compat.v1.reset_default_graph()

red=tflearn.input_data(shape=[None,len(entrenamiento[0])])
red=tflearn.fully_connected(red,10)
red=tflearn.fully_connected(red,10)
red=tflearn.fully_connected(red,len(salida[0]),activation="softmax")
red=tflearn.regression(red)

modelo=tflearn.DNN(red)
modelo.fit(entrenamiento,salida,n_epoch=1000,batch_size=10,show_metric=True)
modelo.save("modelo.tflearn")

def calcular_edad(fecha_nacimiento): ##funcion para calcular la edad#
	    fecha_actual = date.today()
	    resultado = fecha_actual.year - fecha_nacimiento.year
	    resultado -= ((fecha_actual.month, fecha_actual.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
	    return resultado

def scanDPI():
	pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


	Sex='SEXO'
	NacioN='NACIONALIDAD'

	img = cv2.imread('CUI1.jpg')
	image = cv2.resize(img, (900,645))#726,471 # se redimenciona la imagen para tener un estandar"
	imagenplt=cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
	height, width, chanel = image.shape

	crop_imgDPI = image[145:200, 0:290]
	text = pytesseract.image_to_string(crop_imgDPI)
	text = re.sub('[^A-Za-z0-9" "ÁÉÍÓÚ]+', ' ', text)

	crop_imgName = image[130:230, 300:500]
	text1 = pytesseract.image_to_string(crop_imgName,lang='spa')
	text1=re.sub('[^A-Za-z0-9" "ÁÉÍÓÚ]+', ' ', text1)

	crop_imgApellidos = image[232:332, 300:440]
	text2 = pytesseract.image_to_string(crop_imgApellidos,lang='spa')
	text2 = re.sub('[^A-Za-z0-9" "ÁÉÍÓÚ]+', ' ', text2)

	crop_imgSexo = image[336:385, 300:460]
	text3 = pytesseract.image_to_string(crop_imgSexo,lang='spa')
	text3 = re.sub('[^A-Za-z0-9" "ÁÉÍÓÚ]+', ' ', text3)
	text3 = text3.replace('\n',' ')

	crop_imgNacio = image[387:448, 300:480]
	text4 = pytesseract.image_to_string(crop_imgNacio,lang='spa')
	text4 = re.sub('[^A-Za-z0-9" "ÁÉÍÓÚ]+', ' ', text4)

	crop_imgFechaN = image[450:510, 300:490]
	text5 = pytesseract.image_to_string(crop_imgFechaN,lang='spa')
	text5 = re.sub('[^A-Za-z0-9" "ÁÉÍÓÚ]+', ' ', text5)

	indice_g = text3.find(Sex)
	if indice_g != -1:
	    genero = text3[indice_g + 5 : indice_g + 15]
	elif indice_g == -1:
	    Nacionalidad=text3[13:24]

	indice_nacion = text4.find(NacioN)
	if indice_nacion != -1:
	    Nacionalidad = text4[indice_nacion + 13 : indice_g + 24]
	elif indice_nacion == -1:
	    genero=text4[5:15]

	

	Dia=text5[20:22]
	Mes=text5[22:25]
	Año=text5[25:29]

	if Mes=='ENE':
	    mes=1
	    print(mes)
	elif Mes=='FEB':
	    mes=2 
	elif Mes=='MAR':
	    mes=3 
	elif Mes=='ABR':
	    mes=4    
	elif Mes=='MAY':
	    mes=5
	elif Mes=='JUN':
	    mes=6 
	elif Mes=='JUL':
	    mes=7
	elif Mes=='AGO':
	    mes=8     
	elif Mes=='SEP':
	    mes=9 
	elif Mes=='OCT':
	    mes=10 
	elif Mes=='NOV':
	    mes=11 
	elif Mes=='DIC':
	    mes=12 

	fecha_de_nacimento=date(int(Año),int(mes),int(Dia))# (año,mes,día) 
	Edad=calcular_edad(fecha_de_nacimento)

	print(Dia)
	print(Mes)
	print(Año)
	print(Edad)
	#print(New_text)
	#print(indice_g)
	#print(indice_nacion)
	#print(genero)
	print(Nacionalidad)
	#print(height, width)
	print(text)
	print(text1)
	print(text2)
	#print(text3)
	#print(text4)
	print(text5)


def crear_conexion(base_datos):
	try:
		conexion=sqlite3.connect(base_datos)
		return conexion
	except sqlite3.Error as error:
		print("Se ha producido un error al crear la conexión",error)


def crear_tabla(conexion,definicion):
	cursor=conexion.cursor()
	cursor.execute(definicion)
	conexion.commit()

def crear_paciente(conexion,usuario):
	sql='INSERT INTO paciente (dpi,nombre,edad,dosis,tipo_vacuna,fecha_vacuna) VALUES (?,?,?,?,?,?);'
	cursor=conexion.cursor()
	cursor.execute(sql,usuario)
	conexion.commit()

def exportToExcel():
	workbook=Workbook('output.xlsx')
	worksheet=workbook.add_worksheet()
	conn=sqlite3.connect('pacientes.db')
	cursor=conn.cursor()
	data=cursor.execute('SELECT * FROM paciente')
	for i,row in enumerate(data):
		for j,value in enumerate(row):
			worksheet.write(i,j,value)
	workbook.close()

def escuchar():
	with sr.Microphone() as source:
		try:
			print("Habla por favor")
			r.adjust_for_ambient_noise(source,duration=1)
			audio=r.listen(source)
			MiEntrada=r.recognize_google(audio,language="es-ES")
			MiEntrada=MiEntrada.lower()
			#print("Tu: "+MiEntrada)
			return MiEntrada
		except sr.UnknownValueError:
			engine.say("Lo siento, no te entendi")
			engine.runAndWait()

def tagDecision(tag):
	return {
		"vacunaConDosisSegundaSputnik":0,
		"vacunaConDosisSegundaModerna":1,
		"vacunaConDosisSegundaAstrazeneca":2,
		"vacunaConDosisSegundaPfizer":3,
		"vacunaPedidaSputnik":5,
		"vacunaPedidaModerna":6,
		"vacunaPedidaPfizer":7,
		"vacunaPedidaAstrazeneca":8,
		"vacunaDosisPrimera":9,
		"vacunaDosisSegunda":10,
		"tomarFoto":13,
		"vacunaConDosisPrimeraSputnik":15,
		"vacunaConDosisPrimeraModerna":16,
		"vacunaConDosisPrimeraAstrazeneca":17,
		"vacunaConDosisPrimeraPfizer":18
	}.get(tag)

def selectVacuna(option):
	{0:sputnikOption,
	1:modernaOption,
	2:astrazenecaOption,
	3:pfizerOption,
	5:sputnikOption,
	6:modernaOption,
	7:pfizerOption,
	8:astrazenecaOption,
	9:primeraDosis,
	10:segundaDosis,
	15:sputnikOption,
	16:modernaOption,
	17:astrazenecaOption,
	18:pfizerOption
	}[option]()

def sputnikOption():
	global vacunaIndividual
	vacunaIndividual="sputnik"

def modernaOption():
	global vacunaIndividual
	vacunaIndividual="moderna"

def pfizerOption():
	global vacunaIndividual
	vacunaIndividual="pfizer"

def astrazenecaOption():
	global vacunaIndividual
	vacunaIndividual="astrazeneca"

def primeraDosis():
	global dosisIndividual
	dosisIndividual="Primera" #para tener el dato a guardar en la base de datos

def segundaDosis():
	global dosisIndividual
	dosisIndividual="Segunda" #para tener el dato a guardar en la base de datos
	engine.say("Cuál es la fecha en que se coloco la primera dosis de la vacuna")
	engine.runAndWait()
	dias=escucharFecha()
	if vacunaIndividual=="sputnik" or vacunaIndividual=="moderna" or vacunaIndividual=="astrazeneca":
		if dias>28:
			engine.say("Puedes vacunarte")
			engine.runAndWait()
			#Se guarda el dato
		else:
			#No se guarda el dato
			engine.say("Aun no puedes vacunarte")
			engine.runAndWait()
	else:
		if dias>21:
			#Se guarda el dato
			engine.say("Puedes vacunarte")
			engine.runAndWait()
		else:
			#No se guarda el dato
			engine.say("Aun no puedes vacunarte")
			engine.runAndWait()

def aceptarVacuna(tag,dias):
	vacuna=tagDecision(tag)
	if dias>=28 and (vacuna in range(0,2)):
		return True
	elif dias>=21 and vacuna==3:
		return True
	else:
		return False
def escucharFecha():
	with sr.Microphone() as source:
		try:
			print("Decir fecha por favor")
			r.adjust_for_ambient_noise(source,duration=1)
			audio=r.listen(source)
			MiEntrada=r.recognize_google(audio,language="es-ES")
			MiEntrada=MiEntrada.lower()
			today=datetime.date.today()
			print("Fecha: "+MiEntrada)
			if MiEntrada.count("hoy") > 0:
				return today
			day=-1
			day_of_week=-1
			mont=-1
			year=today.year
			for word in MiEntrada.split():
				if word in MONTHS:
					month=MONTHS.index(word)+1
				elif word in DAYS:
					day_of_week=DAYS.index(word)
				elif word.isdigit():
					if int(word)<=31:
						day=int(word)
			d0=date(year,month,day)
			d1=date(today.year,today.month,today.day)
			delta=d1-d0
			return delta.days
			#return datetime.date(month=month,day=day,year=year)
		except sr.UnknownValueError:
			engine.say("Lo siento, no te entendi la fecha")
			engine.runAndWait()

def takePhoto():
	cap = cv2.VideoCapture(0)
#address="https://192.168.1.2:8080/video"
#cap.open(address)
	start=time.time()
	while(cap.isOpened()):
		ret, frame = cap.read()
		gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		cv2.imshow('frame',gray)
		end=time.time()
		elapsedTime=end-start
		if elapsedTime>=4:#cv2.waitKey(1) & 0xFF == ord('q'):
			image=cv2.rotate(frame,cv2.ROTATE_180)
			cv2.imwrite('CUI1.jpg',image)
			break

	cap.release()
	cv2.destroyAllWindows()

def mainBot():
	while True:
		entrada=escuchar() #se descomenta para entrada de voz
		#entrada=input("Tu: ")
		print(entrada)
		if entrada!=None:
			cubeta=[0 for _ in range(len(palabras))]
			entradaProcesada=nltk.word_tokenize(entrada)
			entradaProcesada=[stemmer.stem(palabra.lower()) for palabra in entradaProcesada]
			for palabraIndividual  in entradaProcesada:
				for i,palabra in enumerate(palabras):
					if palabra==palabraIndividual:
						cubeta[i]=1
			resultados=modelo.predict([numpy.array(cubeta)])
			resultadosIndices=numpy.argmax(resultados)
			tag=tags[resultadosIndices]
			print(tag)
			resultTag=tagDecision(tag)
			if resultTag in range(0,4): #Vacunas de segunda dosis
				engine.say("Cuál es la fecha en que se coloco la primera vacuna")
				engine.runAndWait()
				diasVacunacion_primera=escucharFecha()
				if aceptarVacuna(tag,diasVacunacion_primera):
					selectVacuna(resultTag)
					global dosisIndividual
					dosisIndividual="Segunda"
					for tagAux in datos["contenido"]:
						if tagAux["tag"]==tag:
							respuesta=tagAux["respuestas"]
					engine.say(random.choice(respuesta))
					engine.runAndWait()
			elif resultTag in range(5,11):
				selectVacuna(resultTag)
				for tagAux in datos["contenido"]:
						if tagAux["tag"]==tag:
							respuesta=tagAux["respuestas"]
				engine.say(random.choice(respuesta))
				engine.runAndWait()
			elif resultTag in range(14,19): #De lo contrario sera primera dosis de alguna vacuna
				#global dosisIndividual
				dosisIndividual="Primera"
				selectVacuna(resultTag)
				for tagAux in datos["contenido"]:
						if tagAux["tag"]==tag:
							respuesta=tagAux["respuestas"]
				engine.say(random.choice(respuesta))
				engine.runAndWait()
			else:
				for tagAux in datos["contenido"]:
						if tagAux["tag"]==tag:
							respuesta=tagAux["respuestas"]
				engine.say(random.choice(respuesta))
				engine.runAndWait()
			if resultTag==13:#Toma la fotografía
				takePhoto()
				#scanDPI()
				engine.say("Listo, acercate a la estación de vacunación")
				engine.runAndWait()
			print("Vacuna: "+vacunaIndividual)
			print("Dosis: "+str(dosisIndividual))

			
			

mainBot() #Se descomenta para utilizar la IA

#Colocar en el modelo las ventanillas 