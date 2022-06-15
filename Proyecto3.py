import datetime 
from datetime import date, datetime,time
import os, io
from time import sleep, time, time_ns
from tkinter import messagebox
from tkinter.messagebox import showerror
import cv2 as cv
import threading
import sched
import schedule
from playsound import playsound
import sys 
#-----------------------------------------------------
#------------Alerta de distracciones------------------
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
cont=0 
cont_analizador=0
class Actividad:
    def __init__(self,nombre=None,fecha_y_hora_inicio=None,fecha_y_hora_final=None,tipo=None, siguiente=None):
        self.nombre=nombre
        self.f_h_inicio=fecha_y_hora_inicio
        self.f_h_finalizacion=fecha_y_hora_final
        self.tipo=tipo
        self.siguiente=siguiente
        
    def __repr__(self):
        return str("Registro actividad(nombre={}, fecha y hora de inicio={}, fecha y hora de finalización={}, tipo_actividad={} )").format(self.nombre,self.f_h_inicio,self.f_h_finalizacion,self.tipo)

#----------------------------------------------------
#------------Buscar y seleccionar actividad----------

class acciones_actividades:
    def __init__(self):
        self.cabeza=None
        self.cola=None

#***************Agregar actividad****************
    def agregar(self,elemento):
        print("Actividades ya registradas:  ", lista_actividades_disponibles)
        if self.cabeza==None:
            self.cabeza=elemento
        if self.cola!=None:
            self.cola.siguiente=elemento   

        self.cola=elemento  
        lista_actividades_disponibles.append(elemento)

#**************Listar actividades******************
    def listar(self):
        aux = self.cabeza
        while aux !=None:
            print(aux)
            aux = aux.siguiente 
        return None            

#**************Iniciar actividad*******************               
    def iniciar_act(self, nombre,cont_analizador,cont):
        aux = self.cabeza
        while aux!=None:
            if aux.nombre == nombre: #si el nombre recibido es igual al de una actividad registrada
                print ("Este es el registro de la actividad que iniciará: \n",aux,"\n") #imprime la actividad escogida
                ahora=datetime.now() #hora de ahora
                cont_analizador=cont_analizador
                final=aux.f_h_finalizacion
                distraccion=schedule.every(30).seconds.do(distracciones,cont_d,cont_i,cont_b,cont_a)
                s1=schedule.every(60).seconds.do(analizador_emociones_imagen,cont_analizador,final) #son 30 segundos, porque la cuenta regresiva en la función cuenta los otros 30 segundos, completando el minuto         
                while True:
                    if aux.f_h_inicio<=ahora: #si la fecha y hora de inicio de la actividad es mayor a ahora
                        print("Comence la actividad")
                        distraccion_hilo=threading.Thread(target=distracciones,args=(cont_d,cont_i,cont_b,cont_a))
                        emociones_hilo=threading.Thread(target=analizador_emociones_imagen,args=(cont_analizador,final))
                        distraccion_hilo.start()
                        emociones_hilo.start()
                        s1.scheduler.run_pending()
                        distraccion.scheduler.run_pending()
                        cont=cont+1
                        if cont>10:
                            s1=schedule.every(60).seconds.do(analizador_emociones_imagen,cont_analizador,final) #son 30 segundos, porque la cuenta regresiva en la función cuenta los otros 30 segundos, completando el minuto
                            distraccion=schedule.every(30).seconds.do(distracciones,cont_d,cont_i,cont_b,cont_a)                       
                        sleep(1)
                    if ahora >=aux.f_h_finalizacion : #si la fecha y hora de finalizacion de la actividad es menor a ahora
                        print("FIN")
                        #****************************************************************************
                        #***Messagebox para reportar la emoción predominante de toda la actividad****

                        if len(expresiones_toda_la_actividad['felicidad_detectada'])>len(expresiones_toda_la_actividad['enojo_detectado']) and len(expresiones_toda_la_actividad['felicidad_detectada'])>len(expresiones_toda_la_actividad['tisteza/pena_detectada']) and len(expresiones_toda_la_actividad['felicidad_detectada'])>len(expresiones_toda_la_actividad['sorpresa_detectada']): 
                            messagebox.showwarning(title='Reporte emocion predominante',message="La expresión que predominó en la actividad fue: Felicidad")         
                        if len(expresiones_toda_la_actividad['enojo_detectado'])>len(expresiones_toda_la_actividad['felicidad_detectada']) and len(expresiones_toda_la_actividad['enojo_detectado'])>len(expresiones_toda_la_actividad['tisteza/pena_detectada']) and len(expresiones_toda_la_actividad['enojo_detectado'])>len(expresiones_toda_la_actividad['sorpresa_detectada']): 
                            messagebox.showwarning(title='Reporte emocion predominante',message="La expresión que predominó en la actividad fue: Enojo")  
                        if len(expresiones_toda_la_actividad['tisteza/pena_detectada'])>len(expresiones_toda_la_actividad['felicidad_detectada']) and len(expresiones_toda_la_actividad['tisteza/pena_detectada'])>len(expresiones_toda_la_actividad['enojo_detectado']) and len(expresiones_toda_la_actividad['tisteza/pena_detectada'])>len(expresiones_toda_la_actividad['sorpresa_detectada']): 
                            messagebox.showwarning(title='Reporte emocion predominante',message="La expresión que predominó en la actividad fue: Tristeza/pena")               
                        if len(expresiones_toda_la_actividad['sorpresa_detectada'])>len(expresiones_toda_la_actividad['felicidad_detectada']) and len(expresiones_toda_la_actividad['sorpresa_detectada'])>len(expresiones_toda_la_actividad['enojo_detectado']) and len(expresiones_toda_la_actividad['sorpresa_detectada'])>len(expresiones_toda_la_actividad['tisteza/pena_detectada']): 
                            messagebox.showwarning(title='Reporte emocion predominante',message="La expresión que predominó en la actividad fue: Sorpresa")      
    
                        #****************************************************************************
                        #*******Messagebox para reportar la emoción de los primeros 5 minutos *******

                        if len(expresiones_primeros_5m['felicidad_detectada'])>len(expresiones_primeros_5m['enojo_detectado']) and len(expresiones_primeros_5m['felicidad_detectada'])>len(expresiones_primeros_5m['tisteza/pena_detectada']) and len(expresiones_primeros_5m['felicidad_detectada'])>len(expresiones_primeros_5m['sorpresa_detectada']): 
                            messagebox.showwarning(title='Reporte primeros 5 minutos',message="La expresión que predominó durante los primeros 5 minutos de la actividad fue: Felicidad")         
                        if len(expresiones_primeros_5m['enojo_detectado'])>len(expresiones_primeros_5m['felicidad_detectada']) and len(expresiones_primeros_5m['enojo_detectado'])>len(expresiones_primeros_5m['tisteza/pena_detectada']) and len(expresiones_primeros_5m['enojo_detectado'])>len(expresiones_primeros_5m['sorpresa_detectada']): 
                            messagebox.showwarning(title='Reporte primeros 5 minutos',message="La expresión que predominó durante los primeros 5 minutos de la actividad fue: Enojo")  
                        if len(expresiones_primeros_5m['tisteza/pena_detectada'])>len(expresiones_primeros_5m['felicidad_detectada']) and len(expresiones_primeros_5m['tisteza/pena_detectada'])>len(expresiones_primeros_5m['enojo_detectado']) and len(expresiones_primeros_5m['tisteza/pena_detectada'])>len(expresiones_primeros_5m['sorpresa_detectada']): 
                            messagebox.showwarning(title='Reporte primeros 5 minutos',message="La expresión que predominó durante los primeros 5 minutos de la actividad fue: Tristeza/pena")               
                        if len(expresiones_primeros_5m['sorpresa_detectada'])>len(expresiones_primeros_5m['felicidad_detectada']) and len(expresiones_primeros_5m['sorpresa_detectada'])>len(expresiones_primeros_5m['enojo_detectado']) and len(expresiones_primeros_5m['sorpresa_detectada'])>len(expresiones_primeros_5m['tisteza/pena_detectada']): 
                            messagebox.showwarning(title='Reporte primeros 5 minutos',message="La expresión que predominó durante los primeros 5 minutos de la actividad fue: Sorpresa")      

                         #****************************************************************************
                         #*******Messagebox para reportar la emoción de los ultimos 5 minutos ********           
                        if len(expresiones_ultimos_5m['felicidad_detectada'])>len(expresiones_ultimos_5m['enojo_detectado']) and len(expresiones_ultimos_5m['felicidad_detectada'])>len(expresiones_ultimos_5m['tisteza/pena_detectada']) and len(expresiones_ultimos_5m['felicidad_detectada'])>len(expresiones_ultimos_5m['sorpresa_detectada']): 
                            messagebox.showwarning(title='Reporte últimos 5 minutos',message="La expresión que predominó durante los ultimos 5 minutos de la actividad fue: Felicidad")         
                        if len(expresiones_ultimos_5m['enojo_detectado'])>len(expresiones_ultimos_5m['felicidad_detectada']) and len(expresiones_ultimos_5m['enojo_detectado'])>len(expresiones_ultimos_5m['tisteza/pena_detectada']) and len(expresiones_ultimos_5m['enojo_detectado'])>len(expresiones_ultimos_5m['sorpresa_detectada']): 
                            messagebox.showwarning(title='Reporte últimos 5 minutos',message="La expresión que predominó durante los ultimos 5 minutos de la actividad fue: Enojo")  
                        if len(expresiones_ultimos_5m['tisteza/pena_detectada'])>len(expresiones_ultimos_5m['felicidad_detectada']) and len(expresiones_ultimos_5m['tisteza/pena_detectada'])>len(expresiones_ultimos_5m['enojo_detectado']) and len(expresiones_ultimos_5m['tisteza/pena_detectada'])>len(expresiones_ultimos_5m['sorpresa_detectada']): 
                            messagebox.showwarning(title='Reporte últimos 5 minutos',message="La expresión que predominó durante los ultimos 5 minutos de la actividad fue: Tristeza/pena")               
                        if len(expresiones_ultimos_5m['sorpresa_detectada'])>len(expresiones_ultimos_5m['felicidad_detectada']) and len(expresiones_ultimos_5m['sorpresa_detectada'])>len(expresiones_ultimos_5m['enojo_detectado']) and len(expresiones_ultimos_5m['sorpresa_detectada'])>len(expresiones_ultimos_5m['tisteza/pena_detectada']): 
                            messagebox.showwarning(title='Reporte últimos 5 minutos',message="La expresión que predominó durante los ultimos 5 minutos de la actividad fue: Sorpresa")      
                        break #salir de la actividad
                    ahora=datetime.now()
                    sleep(1)

            aux = aux.siguiente
        print("Registro no encontrado")
        return None
        

#----------------------------------------------------------------------
#---Funcion que muestra las acciones a realizar para las actividades---

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
            #***********Agregar actividad brindando los siguientes parametros:************
            nombre = input("Ingrese el nombre de la actividad (no tilde la palabra ): ")
            inicio=input("Ingrese la fecha y hora de inicio de la actividad (formato: (día) del (mes) del (año) a las (horas):(minutos))): ")
            fecha_inicio=datetime.strptime(inicio,'%d del %m del %Y a las %H:%M')
            fin=input("Ingrese la fecha y hora de finalización de la actividad (formato: (día) del (mes) del (año) a las (horas):(minutos))): ")
            fecha_final=datetime.strptime(fin,'%d del %m del %Y a las %H:%M')
            tipo=input("Tipo de actividad (académica o recreativa): ")
            nod = Actividad(nombre,fecha_inicio,fecha_final,tipo)
            ls_actividades.agregar(nod)
        elif num =="2":
            #***********Lista los registros de actividades*********************************
            ls_actividades.listar()
        elif num =="3":
            #***********Inicia una actividad basandose en el nombre dado*******************
            print("Estas son las actividades disponibles: ")
            ls_actividades.listar()
            nombreb = input("Ingrese la actividad que desea iniciar: ")
            cont_me=0
            ls_actividades.iniciar_act(nombreb,cont_me,cont)


#----------------------------------------------------
#----------------Toma imagen-------------------------
class rostro ():
    def __init__(self) -> None:
        pass

    def capturar_imagen(self,vista,cuenta_regresiva):
        # toma la foto en 30 segundos
        if cuenta_regresiva:
            cont=60
            while cont>0:
                print (f'Captura en {cont} segundos emocion...')
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

#.....................................................................................................        
#....................................PARTE DE LAS EMOCIONES...........................................        
#.....................................................................................................

#--------------------------------------------------------------------------
#----Funcion que captura y analiza la fotografía (fue vista en clase)-------
def analizador_emociones_imagen(cont_analizador,final):
    cont_analizador=cont_analizador+1 # contador, este es para llevar una cuenta de los primeros 5 minutos segun las fotos tomadas (5 minutos=5 fotos)
    mi_rostro=rostro() #para llamar a la clase rostro
    imagen=mi_rostro.capturar_imagen(vista=False,cuenta_regresiva=True) #captura la imagen

    from google.cloud import vision # servicio de visión por computadora
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']= r'key.json'
    client=vision.ImageAnnotatorClient()

    with io.open('foto.png','rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.face_detection(image=image)

    faces = response.face_annotations #rostros detectados

    likelihood_name = ('Desconocido', 'muy_poco_probable', 'poco_probable', 'posible', 'probable', 'muy_probable') #probabilidades de las emociones

    faces_list=[]

    for face in faces: 
        #dicccionario con los angulos asociados a la detección de la cara
        face_angles=dict(roll_angle=face.roll_angle,pan_angle=face.pan_angle,tilt_angle=face.tilt_angle) 

        #confianza de detección
        detection_confidence=face.detection_confidence

        #Diccionario de emociones y situaciones
        #Emociones: Alegría, tristeza,enojo,sorpresa
        #Situaciones: baja exposición de la fotografia, usuario con sombrero
        face_expressions=dict(  sonriendo=likelihood_name[face.joy_likelihood],
                                penoso=likelihood_name[face.sorrow_likelihood],
                                enojado=likelihood_name[face.anger_likelihood],
                                sorprendido=likelihood_name[face.surprise_likelihood],
                                baja_exposicion=likelihood_name[face.under_exposed_likelihood],
                                foto_borrosa=likelihood_name[face.blurred_likelihood],
                                sombreros=likelihood_name[face.headwear_likelihood])

        #marco de cara
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
 
    try: # se utiliza try para en caso de que no se detecte un rostro o haya un indexerror con base a x1,y1,x2,y2 

        x1=faces_list[0]['vertices'][0]['x']
        y1=faces_list[0]['vertices'][0]['y']
        x2=faces_list[0]['vertices'][2]['x']
        y2=faces_list[0]['vertices'][2]['y']

        # muestra la imagen al usuario 
        cv.rectangle(imagen,(x1,y1),(x2,y2),(0,255,0),3)
        cv.imshow('Toma de fotografia',imagen)
        cv.waitKey(0)

        #----------Notifica más de un rostro detectado---------------
        if len(faces)>1: # si el largo de la lista de caras detectadas es mayor a uno, lo notifica al usuario
            messagebox.showwarning(title='Alerta',message='Hemos detectado más de un rostro, la fotografía volverá a tomarse')
            emocion1=schedule.every(2).seconds.do(analizador_emociones_imagen,cont_analizador) 
            emocion1.scheduler.run_pending( )
        
        #-----------Evaluacion de emociones y probabilidades---------
        #*****************FELICIDAD**********************************
        if face_expressions['sonriendo']=='muy_probable' or face_expressions['sonriendo']=='probable' or face_expressions['sonriendo']=='posible':
                    print('Felicidad detectada')
                    expresiones_toda_la_actividad['felicidad_detectada'].append(1)
                    print(expresiones_toda_la_actividad['felicidad_detectada'])
                    if cont_analizador <=5: #refiere a que no se han tomado 5 fotos, por lo tanto no han pasado 5 minutos
                        expresiones_primeros_5m['felicidad_detectada'].append(1)
                        print("Agregado a primeros 5m felicidad")
            #**************Aquí empiezan las compparaciones para saber si se está en los últimos 5 minutos de la actividad
                    ahora=datetime.now()
                    ultimos_5=final-ahora
                    minutes =ultimos_5.total_seconds() /60
                    if minutes <6: 
                        print("faltan 5")
                        if minutes<=5:   
                            expresiones_ultimos_5m['felicidad_detectada'].append(1)
                            print("Agregado a ultimos 5m felicidad")

         #*****************PENA O TRISTEZA**********************************           
        if face_expressions['penoso']=='muy_probable' or face_expressions['penoso']=='probable' or face_expressions['penoso']=='posible':
                    print('Tristeza/pena detectada')            
                    expresiones_toda_la_actividad['tisteza/pena_detectada'].append(1)
                    print(expresiones_toda_la_actividad['tisteza/pena_detectada'])
                    if cont_analizador <=5:
                        expresiones_primeros_5m['tisteza/pena_detectada'].append(1)
                        print("Agregado a primeros 5m tristeza")
                        cont_analizador=cont_analizador+1
                #**************Aquí empiezan las compparaciones para saber si se está en los últimos 5 minutos de la actividad        
                    ahora=datetime.now()
                    ultimos_5=final-ahora
                    minutes =ultimos_5.total_seconds() /60
                    if minutes <6:
                        print("faltan 5")
                        if minutes<=5:  
                            expresiones_ultimos_5m['tisteza/pena_detectada'].append(1)
                            print("Agregado a ultimos 5m tristeza")

        #*****************ENOJO***********************************************
        if face_expressions['enojado']=='muy_probable' or face_expressions['enojado']=='probable' or face_expressions['enojado']=='posible':
                    print('Enojo detectado')            
                    expresiones_toda_la_actividad['enojo_detectado'].append(1)
                    print(expresiones_toda_la_actividad['enojo_detectado'])
                    if cont_analizador <=5:
                        expresiones_primeros_5m['enojo_detectado'].append(1)
                        print("Agregado a primeros 5m enojo")
                        cont_analizador=cont_analizador+1
                #**************Aquí empiezan las compparaciones para saber si se está en los últimos 5 minutos de la actividad        
                    ahora=datetime.now()
                    ultimos_5=final-ahora
                    minutes =ultimos_5.total_seconds() /60
                    if minutes <6:
                        print("faltan 5")
                        if minutes<=5:  
                            expresiones_ultimos_5m['enojo_detectado'].append(1)
                            print("Agregado a ultimos 5m enojo")    

         #*****************SORPRESA*******************************************                    
        if face_expressions['sorprendido']=='muy_probable' or face_expressions['sorprendido']=='probable' or face_expressions['sorprendido']=='posible':
                    print('Sorpresa detectada')            
                    expresiones_toda_la_actividad['sorpresa_detectada'].append(1)
                    print(expresiones_toda_la_actividad['sorpresa_detectada'])      
                    if cont_analizador <=5:
                        expresiones_primeros_5m['sorpresa_detectada'].append(1)
                        print("Agregado a primeros 5m sorpresa") 
                        cont_analizador=cont_analizador+1 

                #**************Aquí empiezan las compparaciones para saber si se está en los últimos 5 minutos de la actividad        
                    ahora=datetime.now()
                    ultimos_5=final-ahora
                    minutes =ultimos_5.total_seconds() /60
                    if minutes <6:
                        print("faltan 5")
                        if minutes<=5:  
                            expresiones_ultimos_5m['sorpresa_detectada'].append(1)
                            print("Agregado a ultimos 5m sorpresa")     

        #--------------Analisis de situaciones-----------------------                  
        if face_expressions['baja_exposicion']=='muy_probable' or face_expressions['baja_exposicion']=='probable' or face_expressions['baja_exposicion']=='posible':
                    print('Fotografía con baja exposición a la luz')            
        if face_expressions['foto_borrosa']=='muy_probable' or face_expressions['foto_borrosa']=='probable' or face_expressions['foto_borrosa']=='posible':
                    print('Fotografía borrosa') 
        if face_expressions['sombreros']=='muy_probable' or face_expressions['sombreros']=='probable' or face_expressions['sombreros']=='posible':
                    print('Usted porta un sombrera')         
   
        #si durante la ejecución de la funcion llega la hora final, compare el largo de las listas y emita el reporte
        if ahora>=final:
            print("FIN")
            #Reporte total de la actividad
            if len(expresiones_toda_la_actividad['felicidad_detectada'])>len(expresiones_toda_la_actividad['enojo_detectado']) and len(expresiones_toda_la_actividad['felicidad_detectada'])>len(expresiones_toda_la_actividad['tisteza/pena_detectada']) and len(expresiones_toda_la_actividad['felicidad_detectada'])>len(expresiones_toda_la_actividad['sorpresa_detectada']): 
                messagebox.showwarning(title='Reporte emocion predominante',message="La expresión que predominó en la actividad fue: Felicidad")         
            if len(expresiones_toda_la_actividad['enojo_detectado'])>len(expresiones_toda_la_actividad['felicidad_detectada']) and len(expresiones_toda_la_actividad['enojo_detectado'])>len(expresiones_toda_la_actividad['tisteza/pena_detectada']) and len(expresiones_toda_la_actividad['enojo_detectado'])>len(expresiones_toda_la_actividad['sorpresa_detectada']): 
                messagebox.showwarning(title='Reporte emocion predominante',message="La expresión que predominó en la actividad fue: Enojo")  
            if len(expresiones_toda_la_actividad['tisteza/pena_detectada'])>len(expresiones_toda_la_actividad['felicidad_detectada']) and len(expresiones_toda_la_actividad['tisteza/pena_detectada'])>len(expresiones_toda_la_actividad['enojo_detectado']) and len(expresiones_toda_la_actividad['tisteza/pena_detectada'])>len(expresiones_toda_la_actividad['sorpresa_detectada']): 
                messagebox.showwarning(title='Reporte emocion predominante',message="La expresión que predominó en la actividad fue: Tristeza/pena")               
            if len(expresiones_toda_la_actividad['sorpresa_detectada'])>len(expresiones_toda_la_actividad['felicidad_detectada']) and len(expresiones_toda_la_actividad['sorpresa_detectada'])>len(expresiones_toda_la_actividad['enojo_detectado']) and len(expresiones_toda_la_actividad['sorpresa_detectada'])>len(expresiones_toda_la_actividad['tisteza/pena_detectada']): 
                messagebox.showwarning(title='Reporte emocion predominante',message="La expresión que predominó en la actividad fue: Sorpresa")      
 
            #Reporte primeros 5 minutos
            if len(expresiones_primeros_5m['felicidad_detectada'])>len(expresiones_primeros_5m['enojo_detectado']) and len(expresiones_primeros_5m['felicidad_detectada'])>len(expresiones_primeros_5m['tisteza/pena_detectada']) and len(expresiones_primeros_5m['felicidad_detectada'])>len(expresiones_primeros_5m['sorpresa_detectada']): 
                messagebox.showwarning(title='Reporte primeros 5 minutos',message="La expresión que predominó durante los primeros 5 minutos de la actividad fue: Felicidad")         
            if len(expresiones_primeros_5m['enojo_detectado'])>len(expresiones_primeros_5m['felicidad_detectada']) and len(expresiones_primeros_5m['enojo_detectado'])>len(expresiones_primeros_5m['tisteza/pena_detectada']) and len(expresiones_primeros_5m['enojo_detectado'])>len(expresiones_primeros_5m['sorpresa_detectada']): 
                messagebox.showwarning(title='Reporte primeros 5 minutos',message="La expresión que predominó durante los primeros 5 minutos de la actividad fue: Enojo")  
            if len(expresiones_primeros_5m['tisteza/pena_detectada'])>len(expresiones_primeros_5m['felicidad_detectada']) and len(expresiones_primeros_5m['tisteza/pena_detectada'])>len(expresiones_primeros_5m['enojo_detectado']) and len(expresiones_primeros_5m['tisteza/pena_detectada'])>len(expresiones_primeros_5m['sorpresa_detectada']): 
                messagebox.showwarning(title='Reporte primeros 5 minutos',message="La expresión que predominó durante los primeros 5 minutos de la actividad fue: Tristeza/pena")               
            if len(expresiones_primeros_5m['sorpresa_detectada'])>len(expresiones_primeros_5m['felicidad_detectada']) and len(expresiones_primeros_5m['sorpresa_detectada'])>len(expresiones_primeros_5m['enojo_detectado']) and len(expresiones_primeros_5m['sorpresa_detectada'])>len(expresiones_primeros_5m['tisteza/pena_detectada']): 
                messagebox.showwarning(title='Reporte primeros 5 minutos',message="La expresión que predominó durante los primeros 5 minutos de la actividad fue: Sorpresa")      

            # Reporte ultimos 5 minutos           
            if len(expresiones_ultimos_5m['felicidad_detectada'])>len(expresiones_ultimos_5m['enojo_detectado']) and len(expresiones_ultimos_5m['felicidad_detectada'])>len(expresiones_ultimos_5m['tisteza/pena_detectada']) and len(expresiones_ultimos_5m['felicidad_detectada'])>len(expresiones_ultimos_5m['sorpresa_detectada']): 
                messagebox.showwarning(title='Reporte últimos 5 minutos',message="La expresión que predominó durante los ultimos 5 minutos de la actividad fue: Felicidad")         
            if len(expresiones_ultimos_5m['enojo_detectado'])>len(expresiones_ultimos_5m['felicidad_detectada']) and len(expresiones_ultimos_5m['enojo_detectado'])>len(expresiones_ultimos_5m['tisteza/pena_detectada']) and len(expresiones_ultimos_5m['enojo_detectado'])>len(expresiones_ultimos_5m['sorpresa_detectada']): 
                messagebox.showwarning(title='Reporte últimos 5 minutos',message="La expresión que predominó durante los ultimos 5 minutos de la actividad fue: Enojo")  
            if len(expresiones_ultimos_5m['tisteza/pena_detectada'])>len(expresiones_ultimos_5m['felicidad_detectada']) and len(expresiones_ultimos_5m['tisteza/pena_detectada'])>len(expresiones_ultimos_5m['enojo_detectado']) and len(expresiones_ultimos_5m['tisteza/pena_detectada'])>len(expresiones_ultimos_5m['sorpresa_detectada']): 
                messagebox.showwarning(title='Reporte últimos 5 minutos',message="La expresión que predominó durante los ultimos 5 minutos de la actividad fue: Tristeza/pena")               
            if len(expresiones_ultimos_5m['sorpresa_detectada'])>len(expresiones_ultimos_5m['felicidad_detectada']) and len(expresiones_ultimos_5m['sorpresa_detectada'])>len(expresiones_ultimos_5m['enojo_detectado']) and len(expresiones_ultimos_5m['sorpresa_detectada'])>len(expresiones_ultimos_5m['tisteza/pena_detectada']): 
                messagebox.showwarning(title='Reporte últimos 5 minutos',message="La expresión que predominó durante los ultimos 5 minutos de la actividad fue: Sorpresa")      
            sys.exit()                

    except IndexError: #exepcion de no identificación de rostro o fuera de los márgenes
        cv.imshow('Toma de fotografia',imagen)
        cv.waitKey(0)
        messagebox.showwarning(title='Alerta',message='No hemos detectado ningún rostro, la fotografía volverá a tomarse')
        emocion1=schedule.every(2).seconds.do(analizador_emociones_imagen,cont_analizador) 
        emocion1.scheduler.run_pending( )


#.....................................................................................................        
#....................................PARTE DE LAS DISTRACCIONES.......................................        
#.....................................................................................................


#--------------------------------------------------------------
#---------------Contadores para distracciones------------------
cont_d=0 #para la derecha
cont_i=0 #para la izquierda
cont_b=0 #para abajo
cont_a=0 #para arriba

class rostro_d ():
    def __init__(self) -> None:
        pass

    def capturar_imagen(self,vista,cuenta_regresiva):
        # toma la foto en 30 segundos
        if cuenta_regresiva:
            cont=30
            while cont>0:
                print (f'Captura en {cont} segundos dis...')
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


def analizador_distracciones_imagen(cont_analizador,final):
    cont_analizador=cont_analizador+1 # contador, este es para llevar una cuenta de los primeros 5 minutos segun las fotos tomadas (5 minutos=5 fotos)
    mi_rostro=rostro_d() #para llamar a la clase rostro
    imagen=mi_rostro.capturar_imagen(vista=False,cuenta_regresiva=True) #captura la imagen

    from google.cloud import vision # servicio de visión por computadora
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']= r'key.json'
    client=vision.ImageAnnotatorClient()

    with io.open('foto.png','rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.face_detection(image=image)

    faces = response.face_annotations #rostros detectados

    likelihood_name = ('Desconocido', 'muy_poco_probable', 'poco_probable', 'posible', 'probable', 'muy_probable') #probabilidades de las emociones

    faces_list=[]

    for face in faces: 
        #dicccionario con los angulos asociados a la detección de la cara
        face_angles=dict(roll_angle=face.roll_angle,pan_angle=face.pan_angle,tilt_angle=face.tilt_angle) 

        #confianza de detección
        detection_confidence=face.detection_confidence

        #Diccionario de emociones y situaciones
        #Emociones: Alegría, tristeza,enojo,sorpresa
        #Situaciones: baja exposición de la fotografia, usuario con sombrero
        face_expressions=dict(  sonriendo=likelihood_name[face.joy_likelihood],
                                penoso=likelihood_name[face.sorrow_likelihood],
                                enojado=likelihood_name[face.anger_likelihood],
                                sorprendido=likelihood_name[face.surprise_likelihood],
                                baja_exposicion=likelihood_name[face.under_exposed_likelihood],
                                foto_borrosa=likelihood_name[face.blurred_likelihood],
                                sombreros=likelihood_name[face.headwear_likelihood])

        #marco de cara
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
 
    try: # se utiliza try para en caso de que no se detecte un rostro o haya un indexerror con base a x1,y1,x2,y2 

        x1=faces_list[0]['vertices'][0]['x']
        y1=faces_list[0]['vertices'][0]['y']
        x2=faces_list[0]['vertices'][2]['x']
        y2=faces_list[0]['vertices'][2]['y']

        # muestra la imagen al usuario 
        cv.rectangle(imagen,(x1,y1),(x2,y2),(0,255,0),3)
        cv.imshow('Toma de fotografia',imagen)
        cv.waitKey(0)

        #----------Notifica más de un rostro detectado---------------
        if len(faces)>1: # si el largo de la lista de caras detectadas es mayor a uno, lo notifica al usuario
            messagebox.showwarning(title='Alerta',message='Hemos detectado más de un rostro, la fotografía volverá a tomarse')
            emocion1=schedule.every(2).seconds.do(analizador_distracciones_imagen,cont_analizador) 
            emocion1.scheduler.run_pending( )
    except IndexError: #exepcion de no identificación de rostro o fuera de los márgenes
        cv.imshow('Toma de fotografia',imagen)
        cv.waitKey(0)
        messagebox.showwarning(title='Alerta',message='No hemos detectado ningún rostro, la fotografía volverá a tomarse')
        emocion1=schedule.every(2).seconds.do(analizador_distracciones_imagen,cont_analizador) 
        emocion1.scheduler.run_pending( )




#-------------------------------------------------------------
#---------------Función de distracciones----------------------
def distracciones(cont_d,cont_i,cont_b,cont_a):
    toma_distraccion=rostro_d()
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
