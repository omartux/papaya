#!/usr/bin/env python
# -*- coding: utf-8 -*-
# UANCV 
# Cesar Paredes Oscalla
# Ing. Mecatronica 

import cv2 as cv
import numpy as np
from datetime import date, datetime #importa libreria dia de hoy fechas
import os.path
import pandas as pd

cv.namedWindow('normal', cv.WINDOW_NORMAL)
cv.resizeWindow('normal', 320,240)
cv.namedWindow('gris', cv.WINDOW_NORMAL)
cv.resizeWindow('gris', 320,240)
cv.namedWindow('blur', cv.WINDOW_NORMAL)
cv.resizeWindow('blur', 320,240)
cv.namedWindow('mask', cv.WINDOW_NORMAL)
cv.resizeWindow('mask', 320,240)
cv.namedWindow('canny', cv.WINDOW_NORMAL)
cv.resizeWindow('canny', 320,240)
cv.namedWindow('LAB', cv.WINDOW_NORMAL)
cv.resizeWindow('LAB', 320,240)
cv.namedWindow('HSV', cv.WINDOW_NORMAL)
cv.resizeWindow('HSV', 320,240)
cv.namedWindow('thresh', cv.WINDOW_NORMAL)
cv.resizeWindow('thresh', 320,240)
cv.namedWindow('RESULT', cv.WINDOW_NORMAL)
cv.resizeWindow('RESULT', 320,240)
cv.namedWindow('L', cv.WINDOW_NORMAL)
cv.resizeWindow('L', 320,240)
cv.namedWindow('A', cv.WINDOW_NORMAL)
cv.resizeWindow('A', 320,240)
cv.namedWindow('B', cv.WINDOW_NORMAL)
cv.resizeWindow('B', 320,240)
cv.namedWindow('H', cv.WINDOW_NORMAL)
cv.resizeWindow('H', 320,240)
cv.namedWindow('S', cv.WINDOW_NORMAL)
cv.resizeWindow('S', 320,240)
cv.namedWindow('V', cv.WINDOW_NORMAL)
cv.resizeWindow('V', 320,240)
cv.namedWindow('centro', cv.WINDOW_NORMAL)
cv.resizeWindow('centro', 320,240)
#en caso de mas camaras cambiar el indice
#cv2.VideoCapture(cv2.CAP_DSHOW + camera_index)
#cap = cv.VideoCapture(1)
#camera_index = 1
#cap = cv.VideoCapture(cv.CAP_DSHOW + camera_index)
#cap = cv.VideoCapture('demo.mp4')
#para usar stream usar la linea siguiente
cap = cv.VideoCapture('video/faja.mp4')

if not cap.isOpened():
    raise IOError("No se puede abrir Camara Web")
    exit()

contador = 0

arriba = False
abajo = True

frame_counter = 0

if os.path.isfile('./valores_papaya.csv')==False:
    archivo = open('valores_papaya.csv', "a") #apertura de archivo
    cadena = ('fecha_actual;tiempo_actual;papaya_id;Canal_L;Canal_A;Canal_B;Canal_H;Canal_S;Canal_V;Area;Calidad;Tamano\n')
    archivo.write(cadena) #escritura de los datos
    archivo.close() #cerrado del archivo

while(True): #Bucle infinito
    umbrali = 255/4
    umbrals = 255
    edges = 0
    objetos = 10
    grosor = 5
    kernel = 3


    ret,frame = cap.read()
    frame_counter += 1
    #para resetear el contador de stream de camara web
    if frame_counter == cap.get(cv.CAP_PROP_FRAME_COUNT):
        frame_counter = 0 #reiniciar en el frame 0
        cap.set(cv.CAP_PROP_POS_FRAMES, 0)
        
    w = cap.get(3)
    h = cap.get(4)
    fps = cap.get(5)
    
    normal = frame.copy() 
    gris = cv.cvtColor(normal, cv.COLOR_BGR2GRAY)
    gris = cv.medianBlur(gris,5)

    
    blur = cv.GaussianBlur(gris, (5, 5), 0)
    canny = cv.Canny(blur,umbrali,umbrals,kernel) 
   
    (contornos,_) = cv.findContours(canny.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if len(contornos) > 0 and len(contornos) < 5:
        
        canny = cv.drawContours(canny, contornos[0], -1, (255,255,255), thickness = grosor)  
        thresh = cv.threshold(canny, 5, 255, cv.THRESH_BINARY)[1]
        contours = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        big_contour = max(contours, key=cv.contourArea)
   
        mask = np.zeros(normal.shape[:2], np.uint8)
        mask = cv.drawContours(mask, [big_contour], 0, (255,255,255), cv.FILLED)
        
        #centro = mask.copy()
        
        result = cv.bitwise_and(normal, normal, mask=mask)
        
        LAB = cv.cvtColor(result, cv.COLOR_BGR2LAB)
        HSV = cv.cvtColor(result, cv.COLOR_BGR2HSV)
        
        L,A,B = cv.split(LAB)
        H,S,V = cv.split(HSV)
        
        cv.imshow('normal',normal)
        cv.imshow('canny',canny)
        cv.imshow('blur',blur)
        cv.imshow('gris',gris)
        cv.imshow('thresh',thresh)
        cv.imshow('mask',mask)
        cv.imshow('RESULT',result)
        cv.imshow('LAB',LAB)
        cv.imshow('HSV',HSV)
        cv.imshow('L',L)
        cv.imshow('A',A)
        cv.imshow('B',B)
        cv.imshow('H',H)
        cv.imshow('S',S)
        cv.imshow('V',V)
        #cv.imshow('centro',centro)
       
        Area= np.sum(mask) # suma de pixeles en la matriz de mascara
        Area=int(Area)
              
        promedio = int(np.mean(mask))
        umbral = 40
        
        #rutina para deteccion de flanco de subida
        
        if promedio < umbral :
            #print (False)
            estado = False
            abajo = True
    
        if promedio > umbral :
            #print (True)
            estado = True
            arriba = True
           
            if arriba == 1 and abajo ==1:
                contador += 1
                print (contador)
                abajo = 0
                arriba = 0 #fin de rutina para deteccion de flanco de bajada
                #calculo de promedios de los canales encerrados por el borde
                
                centro = mask.copy()
                m = cv.moments(centro)
                
                x = m['m10']/m['m00']
                y = m['m01']/m['m00']
                print('x=',x, 'y=',y)
                
                
                color = (0, 0, 0) #negro
                grosor_circulo = 4

                #cv.circle(centro, (int(x),int(y)), 255, 0, 0)
                #image = cv2.circle(image, center_coordinates, radius, color, thickness)
                cv.circle(centro, (int(x),int(y)), 20, color, grosor_circulo)
                font = cv.FONT_HERSHEY_SIMPLEX
                # org                  
                # fontScale
                fontScale = 1
                   
                 
                # Line thickness of 2 px
                grosor_numero = 4
                   
                # Using cv2.putText() method
                image = cv.putText(centro, str(contador), (int(x+30),int(y+10)), font, fontScale, color, grosor_numero, cv.LINE_AA)
                   
                # Displaying the image
               
                
                cv.imshow('centro',centro)
                
                mL = np.mean(L)
                mA = np.mean(A)
                mB = np.mean(B)
            
                mH = np.mean(H)
                mS = np.mean(S)
                mV = np.mean(V)
              
                calidad = 50 #paramtro de calidad
                tamano = 20000000 #parametro de tamano
                
                if mV>calidad:
                    qa = "ok"
                if mV<calidad:
                    qa = "no-ok"
                
                if tamano > Area:
                    qat = "medium"
                if tamano < Area:
                    qat = "small"
                
                hoy = date.today() #rutina de fechas
                ahora = datetime.now()
                tiempo_actual = ahora.strftime("%H:%M:%S")
                

                archivo = open('valores_papaya.csv', "a") #apertura de archivo
                cadena = (str(hoy)+";"+str(tiempo_actual)+";"+str('00_'+str(contador))+
                          ";"+str(mL)+";"+str(mA)+";"+str(mB)+
                          ";"+str(mH)+";"+str(mS)+";"+str(mV)+
                          ";"+str(Area)+";"+str(qa)+";"+str(qat)+"\n")
                archivo.write(cadena) #escritura de los datos
                archivo.close() #cerrado del archivo
                
                path = ".\salida\\" #carpeta de salida de imagenes
                name = str(contador)
                print (path+name) 
                #rutina de escritura de imagenes 
                cv.imwrite(str(path+name)+'_result.jpg', result)
                cv.imwrite(str(path+name)+'_gris.jpg', gris)
                cv.imwrite(str(path+name)+'_blur.jpg', blur)
                cv.imwrite(str(path+name)+'_edges.jpg', edges )
                cv.imwrite(str(path+name)+'_mask.jpg',mask)
                cv.imwrite(str(path+name)+'_L.jpg',L)
                cv.imwrite(str(path+name)+'_A.jpg',A)
                cv.imwrite(str(path+name)+'_B.jpg',B)
                cv.imwrite(str(path+name)+'_H.jpg',H)
                cv.imwrite(str(path+name)+'_S.jpg',S)
                cv.imwrite(str(path+name)+'_V.jpg',V)
                cv.imwrite(str(path+name)+'_centroide.jpg',centro)
                #img = cv.imread((".\salida\\"+"_mask.jpg"),0)
  
    else:
        pass

     
    if cv.waitKey(1) & 0xFF == ord('x'): # se cierra con x 
        break  
read_file = pd.read_csv ('valores_papaya.csv', sep=';')
read_file.to_excel ('valores_papaya.xlsx', index = None, header=True)
    

# al terminar cerrar captura
cap.release()
cv.destroyAllWindows() 
