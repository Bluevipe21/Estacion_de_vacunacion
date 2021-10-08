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
#nltk.download('punkt')

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
		"vacunaDosisSegunda":10
	}.get(tag)

def selectVacuna(option):
	{5:sputnikOption
	}[option]()

def sputnikOption():
	print("Opcion sputnik seleccionada")

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
			print("tag:"+tag)
			resultTag=tagDecision(tag)
			if resultTag in range(0,4): #Vacunas de segunda dosis
				engine.say("Cuál es la fecha en que se coloco la primera vacuna")
				engine.runAndWait()
				diasVacunacion_primera=escucharFecha()
				if aceptarVacuna(tag,diasVacunacion_primera):
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
			else: #De lo contrario sera primera dosis de alguna vacuna
				for tagAux in datos["contenido"]:
						if tagAux["tag"]==tag:
							respuesta=tagAux["respuestas"]
				engine.say(random.choice(respuesta))
				engine.runAndWait()

			
			

mainBot() #Se descomenta para utilizar la IA

#Colocar en el modelo las ventanillas 