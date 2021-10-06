import sqlite3

#Establecer conexión con la base de datos
conexion=sqlite3.connect("BDVacunacion")

cursor=conexion.cursor()

instruccionSQL="CREATE TABLE usuarios(dpi VARCHAR(13),nombre VARCHAR(30),apellido VARCHAR(50),fechaVacuna1 TIMESTAMP,fechaVacuna2 TIMESTAMP)"

cursor.execute(instruccionSQL)
"""
inserts=[
((input('id: ')),input('Nombre: '),input('Apellido: ')),
(3,'Juan','Perez')
]

cursor.executemany("INSERT INTO usuarios VALUES(?,?,?)",inserts)

"""
#cursor.execute("SELECT * FROM usuarios")
#contenido=cursor.fetchall()

#for elemento in contenido:
#	print(elemento[1].encode("ascii"))

conexion.commit()
conexion.close()
