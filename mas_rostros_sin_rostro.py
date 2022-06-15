from datetime import date, datetime,time
from operator import index
import os, io
from time import sleep, time, time_ns
from tkinter import messagebox
from tkinter.messagebox import showerror
import cv2 as cv
import threading
import sched
import schedule
from playsound import playsound

#-------Alerta de distracciones--------------
def alerta():
    alerta_sonido='alerta1.mp3'
    playsound(alerta_sonido)
    messagebox.showwarning(title='Alerta de descooncentración',message='Hemos detectado que has perdido la concentración, por favor presta atención a la actividad')

#------------------------------------------------------
#-------DICCIONARIO PARA CONTADOR DE EMOCIONES---------
expresiones_toda_la_actividad = { #diccionario que contiene las listas de las expresiones
        'felicidad_detectada' : [], #felicidad
        'tisteza/pena_detectada' : [], #tristeza
        'enojo_detectado' : [],  #enojo
        'sorpresa_detectada' : [], #sorpresa
         }
expresiones_primeros_5m={ #diccionario que contiene las listas de las expresiones de los primeros 5 minutos
        'felicidad_detectada' : [], #felicidad
        'tisteza/pena_detectada' : [], #tristeza
        'enojo_detectado' : [],  #enojo
        'sorpresa_detectada' : [], #sorpresa
         }    
expresiones_ultimos_5m={ #diccionario que contiene las listas de las expresiones de los primeros 5 minutos
        'felicidad_detectada' : [], #felicidad
        'tisteza/pena_detectada' : [], #tristeza
        'enojo_detectado' : [],  #enojo
        'sorpresa_detectada' : [], #sorpresa
         }          
#-----------------------------------------------------
#----------------Lista de actividades-----------------
lista_actividades_disponibles=[]
#-----------------------------------------------------
#-----------------Actividades-------------------------
class Actividad:
    def __init__(self,nombre=None,fecha_y_hora_inicio=None,fecha_y_hora_final=None,tipo=None, siguiente=None):
        self.nombre=nombre
        self.f_h_inicio=fecha_y_hora_inicio
        self.f_h_finalizacion=fecha_y_hora_final
        self.tipo=tipo
        self.siguiente=siguiente
        
    def __repr__(self):
        return str("Registro actividad(nombre={}, fecha y hora de inicio={}, fecha y hora de finalización={}, tipo_actividad={} )").format(self.nombre,self.f_h_inicio,self.f_h_finalizacion,self.tipo)

#inicio=datetime(2022,6,11,16,43)
#fin=datetime(2022,6,11,16,44)
#nod=Actividad("Estudiar Examen Mate",inicio,fin,"Academica")

#print(nod)
#----------------------------------------------------
#------------Buscar y seleccionar actividad----------
class acciones_actividades:
    def __init__(self):
        self.cabeza=None
        self.cola=None
#----------Listo
    def agregar(self,elemento):
        print("Actividades ya registradas:  ", lista_actividades_disponibles)
        if self.cabeza==None:
            self.cabeza=elemento
        if self.cola!=None:
            self.cola.siguiente=elemento   

        self.cola=elemento  
        lista_actividades_disponibles.append(elemento)

    def listar(self):
        aux = self.cabeza
        while aux !=None:
            print(aux)
            aux = aux.siguiente 
        return None                  
                
    def buscar(self, nombre):
        aux = self.cabeza
        while aux!=None:
            if aux.nombre == nombre:
                print (aux)
                #Toma cada 30
                ahora=datetime.now()
                #print(me())
                emocion=schedule.every(5).seconds.do(me)
                #distaccion=schedule.every(30).seconds.do(distracciones(cont_d,cont_i,cont_b,cont_a))
               
                cont=0
                while True:
                    if aux.f_h_inicio<ahora:
                        print("Comence la actividad")
                        emocion.scheduler.run_pending()
                        distaccion=schedule.every(30).seconds.do(distracciones(cont_d,cont_i,cont_b,cont_a))
                        distaccion.scheduler.run_pending(cont_d,cont_i,cont_b,cont_a)
                        cont=cont+1
                        if cont>10:
                            emocion=schedule.every(60).seconds.do(me)
                            distaccion=schedule.every(30).seconds.do(distracciones(cont_d,cont_i,cont_b,cont_a))
                        sleep(1)

                    if aux.f_h_finalizacion < ahora :
                        print("FIN")
                        break
                    ahora=datetime.now()
                    sleep(1)

            aux = aux.siguiente
        return None

#************************************************************
def inicio_actividades():
    ls_actividades = acciones_actividades()
    while(True):
        print("\n"+
              "-----------------------Menu----------------------------------------\n"+
              "\n"+
              "1. Agregar una actividad\n"+
              "2. Listar actividades existentes\n"+
              "3. Iniciar una actividad\n")
        num = input("Ingrese la opcion: ")
        if num == "1":
            nombre = input("Ingrese el nombre de la actividad (no tilde la palabra ): ")
            inicio=input("Ingrese la fecha y hora de inicio de la actividad (formato: (día) del (mes) del (año) a las (horas):(minutos))): ")
            fecha_inicio=datetime.strptime(inicio,'%d del %m del %Y a las %H:%M')
            fin=input("Ingrese la fecha y hora de finalización de la actividad (formato: (día) del (mes) del (año) a las (horas):(minutos))): ")
            fecha_final=datetime.strptime(fin,'%d del %m del %Y a las %H:%M')
            tipo=input("Tipo de actividad (académica o educativa): ")
            nod = Actividad(nombre,fecha_inicio,fecha_final,tipo)
            ls_actividades.agregar(nod)
        elif num =="2":
            ls_actividades.listar()
        elif num =="3":
            print("Estas son las actividades disponibles: ")
            ls_actividades.listar()
            nombreb = input("Ingrese la actividad que desea iniciar: ")
            ls_actividades.buscar(nombreb)
            #if result is not None:
             #   print (result)
            #else:
             #   print("Registro no encontrado")



#----------------------------------------------------
#----------------Toma imagen-------------------------
class rostro ():
    def __init__(self) -> None:
        pass

    def capturar_imagen(self,vista,cuenta_regresiva):
        # toma la foto en 30 segundos

        if cuenta_regresiva:
            cont=5
            while cont>0:
                print (f'Captura en {cont} segundos...')
                sleep(1)
                cont-=1

        camara = cv.VideoCapture(0)
        leido, imagen = camara.read()
        camara.release()

        if leido == True:
            cv.imwrite("foto.png", imagen)
            if vista:
                cv.imshow('Toma de fotografia',imagen)
                cv.waitKey(0)
        else:
            showerror(
                title='Error en la toma de imagen', 
                message='No fue posible capturar la imagen con esta dispositivo!')
        return imagen


def tarea_paralela(estado):
    mi_rostro=rostro()
    while estado[0]:
            print("Toma de imagen: ",mi_rostro.capturar_imagen(vista=False,cuenta_regresiva=False))
            sleep(5)



def menu():
    estado=[True]
    parametros=[estado]
    proceso=threading.Thread(target=tarea_paralela,args=parametros)
    proceso.start()


#----------Leida de rostro--------------------------------------
def me():
    mi_rostro=rostro()
    imagen=mi_rostro.capturar_imagen(vista=False,cuenta_regresiva=True)

    from google.cloud import vision
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']= r'key.json'
    client=vision.ImageAnnotatorClient()

    with io.open('foto.png','rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.face_detection(image=image)

    faces = response.face_annotations

    likelihood_name = ('Desconocido', 'muy_poco_probable', 'poco_probable', 'posible', 'probable', 'muy_probable')

    faces_list=[]



    for face in faces:
        #dicccionario con los angulos asociados a la detección de la cara
        face_angles=dict(roll_angle=face.roll_angle,pan_angle=face.pan_angle,tilt_angle=face.tilt_angle)

        #confianza de detección (tipo float)
        detection_confidence=face.detection_confidence

        #Probabilidad de Expresiones
        #Emociones: Alegría, tristeza,enojo,sorpresa
        #Situaciones: baja exposición de la fotografia, usuario con sombrero
        face_expressions=dict(  sonriendo=likelihood_name[face.joy_likelihood],
                                penoso=likelihood_name[face.sorrow_likelihood],
                                enojado=likelihood_name[face.anger_likelihood],
                                sorprendido=likelihood_name[face.surprise_likelihood],
                                baja_exposicion=likelihood_name[face.under_exposed_likelihood],
                                foto_borrosa=likelihood_name[face.blurred_likelihood],
                                sombreros=likelihood_name[face.headwear_likelihood])

        #polígono de marco de cara
        vertices=[]
        for vertex in face.bounding_poly.vertices:
            vertices.append (dict (x=vertex.x, y=vertex.y))

        #Cuadro de reconocimiento
        face_dict=dict( face_angles=face_angles,
                        detection_confidence=detection_confidence,
                        face_expressions=face_expressions,
                        vertices=vertices
                        )
        faces_list.append(face_dict)
 
    try:
        x1=faces_list[0]['vertices'][0]['x']
        y1=faces_list[0]['vertices'][0]['y']
        x2=faces_list[0]['vertices'][2]['x']
        y2=faces_list[0]['vertices'][2]['y']



        cv.rectangle(imagen,(x1,y1),(x2,y2),(0,255,0),3)

        cv.imshow('Toma de fotografia',imagen)

        cv.waitKey(0)

        if len(faces)>1:
            messagebox.showwarning(title='Alerta',message='Hemos detectado más de un rostro, la fotografía volverá a tomarse')
            foto_2=mi_rostro.capturar_imagen(vista=False,cuenta_regresiva=True)
        

        if face_expressions['sonriendo']=='muy_probable' or face_expressions['sonriendo']=='probable' or face_expressions['sonriendo']=='posible':
                    print('Felicidad detectada')
                    expresiones_toda_la_actividad['felicidad_detectada'].append(1)
                    print(expresiones_toda_la_actividad['felicidad_detectada'])
        if face_expressions['penoso']=='muy_probable' or face_expressions['penoso']=='probable' or face_expressions['penoso']=='posible':
                    print('Tristeza/pena detectada')            
                    expresiones_toda_la_actividad['tisteza/pena_detectada'].append(1)
                    print(expresiones_toda_la_actividad['tisteza/pena_detectada'])
        if face_expressions['enojado']=='muy_probable' or face_expressions['enojado']=='probable' or face_expressions['enojado']=='posible':
                    print('Enojo detectado')            
                    expresiones_toda_la_actividad['enojo_detectado'].append(1)
                    print(expresiones_toda_la_actividad['enojo_detectado'])
        if face_expressions['sorprendido']=='muy_probable' or face_expressions['sorprendido']=='probable' or face_expressions['sorprendido']=='posible':
                    print('Sorpresa detectada')            
                    expresiones_toda_la_actividad['sorpresa_detectada'].append(1)
                    print(expresiones_toda_la_actividad['sorpresa_detectada'])           
        if face_expressions['baja_exposicion']=='muy_probable' or face_expressions['baja_exposicion']=='probable' or face_expressions['baja_exposicion']=='posible':
                    print('Fotografía con baja exposición a la luz')            
        if face_expressions['foto_borrosa']=='muy_probable' or face_expressions['foto_borrosa']=='probable' or face_expressions['foto_borrosa']=='posible':
                    print('Fotografía borrosa') 
        if face_expressions['sombreros']=='muy_probable' or face_expressions['sombreros']=='probable' or face_expressions['sombreros']=='posible':
                    print('Usted porta un sombrera')         

        #Comparaciones            
        if len(expresiones_toda_la_actividad['felicidad_detectada'])>len(expresiones_toda_la_actividad['enojo_detectado']) and len(expresiones_toda_la_actividad['felicidad_detectada'])>len(expresiones_toda_la_actividad['tisteza/pena_detectada']) and len(expresiones_toda_la_actividad['felicidad_detectada'])>len(expresiones_toda_la_actividad['sorpresa_detectada']): 
            print("más felicidad")         
        if len(expresiones_toda_la_actividad['enojo_detectado'])>len(expresiones_toda_la_actividad['felicidad_detectada']) and len(expresiones_toda_la_actividad['enojo_detectado'])>len(expresiones_toda_la_actividad['tisteza/pena_detectada']) and len(expresiones_toda_la_actividad['enojo_detectado'])>len(expresiones_toda_la_actividad['sorpresa_detectada']): 
            print("más enojo")  
        if len(expresiones_toda_la_actividad['tisteza/pena_detectada'])>len(expresiones_toda_la_actividad['felicidad_detectada']) and len(expresiones_toda_la_actividad['tisteza/pena_detectada'])>len(expresiones_toda_la_actividad['enojo_detectado']) and len(expresiones_toda_la_actividad['tisteza/pena_detectada'])>len(expresiones_toda_la_actividad['sorpresa_detectada']): 
            print("más tristeza/pena")               
        if len(expresiones_toda_la_actividad['sorpresa_detectada'])>len(expresiones_toda_la_actividad['felicidad_detectada']) and len(expresiones_toda_la_actividad['sorpresa_detectada'])>len(expresiones_toda_la_actividad['enojo_detectado']) and len(expresiones_toda_la_actividad['sorpresa_detectada'])>len(expresiones_toda_la_actividad['tisteza/pena_detectada']): 
            print("más sorpresa") 

    except IndexError:
        cv.imshow('Toma de fotografia',imagen)
        cv.waitKey(0)
        messagebox.showwarning(title='Alerta',message='No hemos detectado ningún rostro, la fotografía volverá a tomarse')
        emocion1=schedule.every(2).seconds.do(me)
        emocion1.scheduler.run_pending()
#--------------------------------------------------------------
#---------------Contadores para distracciones------------------
cont_d=0 #para la derecha
cont_i=0 #para la izquierda
cont_b=0 #para abajo
cont_a=0 #para arriba

#-------------------------------------------------------------
#---------------Función de distracciones----------------------
def distracciones(cont_d,cont_i,cont_b,cont_a):
    toma_distraccion=rostro()
    imagen=toma_distraccion.capturar_imagen(vista=False,cuenta_regresiva=True)

    from google.cloud import vision
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']= r'key.json'
    client=vision.ImageAnnotatorClient()

    with io.open('foto.png','rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.face_detection(image=image)

    faces = response.face_annotations

    faces_list=[]
    
    #******deteccion de mas rostros******* 
    #notifica al usuario por medio de una messagebox
    if len(faces)>1:
       messagebox.showwarning(title='Alerta',message='Hemos detectado más de un rostro, la fotografía volverá a tomarse')
       dis=schedule.every(5).seconds.do(distracciones(cont_d,cont_i,cont_b,cont_a)) 

    for face in faces:
        #dicccionario con los angulos asociados a la detección de la cara
        face_angles=dict(roll_angle=face.roll_angle,pan_angle=face.pan_angle,tilt_angle=face.tilt_angle)

        #confianza de detección (tipo float)
        detection_confidence=face.detection_confidence


        #polígono de marco de cara
        vertices=[]
        for vertex in face.bounding_poly.vertices:
            vertices.append (dict (x=vertex.x, y=vertex.y))

        #Cuadro de reconocimiento
        face_dict=dict( face_angles=face_angles,
                        detection_confidence=detection_confidence,
                        vertices=vertices
                        )
        faces_list.append(face_dict)

    x1=faces_list[0]['vertices'][0]['x']
    y1=faces_list[0]['vertices'][0]['y']
    x2=faces_list[0]['vertices'][2]['x']
    y2=faces_list[0]['vertices'][2]['y']

    cv.rectangle(imagen,(x1,y1),(x2,y2),(0,255,0),3)

    cv.imshow('Toma de fotografia',imagen)

    cv.waitKey(0)

    if face_angles['pan_angle'] <-35: # distraccion a la derecha
        print("la persona está viendo hacia la derecha")
        while True:
            if cont_d ==5:
                print("Alerta")
                print(alerta())
                sleep(1) 
                cont_d=0
                dis=schedule.every(5).seconds.do(distracciones(cont_d,cont_i,cont_b,cont_a)) 
            elif cont_d < 5:
                print("Contando derecha")
                cont_d=cont_d+1
                dis=schedule.every(5).seconds.do(distracciones(cont_d,cont_i,cont_b,cont_a))
                dis.scheduler.run_pending(cont_d,cont_i,cont_b,cont_a)   
    elif face_angles['pan_angle'] > 35: # distraccion a la izquierda
        print("la persona está viendo hacia la izquierda")
        while True:
            if cont_i ==5:
                print("Alerta")
                print(alerta())
                sleep(1)   
                cont_i=0
                dis=schedule.every(5).seconds.do(distracciones(cont_d,cont_i,cont_b,cont_a)) 
            elif cont_i < 5:
                print("Contando izquierda")
                cont_i=cont_i+1
                dis=schedule.every(5).seconds.do(distracciones(cont_d,cont_i,cont_b,cont_a))
                dis.scheduler.run_pending(cont_d,cont_i,cont_b,cont_a)   

    elif face_angles['tilt_angle'] <-16: #distraccion hacia abajo 
        print("la persona está viendo hacia la abajo")
        while True:
            if cont_b ==5:
                print("Alerta")
                print(alerta())
                sleep(1)   
                cont_b=0
                dis=schedule.every(5).seconds.do(distracciones(cont_d,cont_i,cont_b,cont_a)) 
            elif cont_b < 5:
                print("Contando abajo")
                cont_b=cont_b+1
                dis=schedule.every(5).seconds.do(distracciones(cont_d,cont_i,cont_b,cont_a))
                dis.scheduler.run_pending(cont_d,cont_i,cont_b,cont_a) 

    elif face_angles['tilt_angle'] >16: #distraccion hacia arriba           
        print("la persona está viendo hacia la arriba")
        while True:
            if cont_a ==5:
                print("Alerta")
                print(alerta())
                sleep(1) 
                cont_a=0
                  
            elif cont_a < 5:
                print("Contando arriba")
                cont_a=cont_a+1
                dis=schedule.every(5).seconds.do(distracciones(cont_d,cont_i,cont_b,cont_a))
                dis.scheduler.run_pending(cont_d,cont_i,cont_b,cont_a) 


print(inicio_actividades())


#Ocupo hacer un proceso con hilos para ejecutar paralelamente el proceso de emociones y distracciones
#Realizar el reporte 
#diccionario primeros 5 minutos, las listas 
#comparaciones con un contador de promeros 5==5, 
#ir agregando a parte del actual diccionario, al diccionario primeros 5
#imprimir "La emocion que predominó en los primeros 5 minutos fue: (mayor largo del dic_primeros_5)"
#imprimir "La emocion que más predominó fue:(mayor largo del dic_actual) "
#if hora actual más 5 == hora final
#iniciar un contador para esos últimos 5 minutos
#un diccionario para ese contador
#imprimir "La emocion que predominó en los últimos 5 minutos fue:(mayor de esa lista)
#Realizar el gráfico

