import cv2
import numpy as np
import math

cap = cv2.VideoCapture('Autos.mp4')

sustractor = cv2.createBackgroundSubtractorMOG2(history=150, varThreshold=30, detectShadows=True)

# Variables para la lógica de conteo
conteo_vehiculos = 0
linea_conteo_y = 500 
offset = 15
autos_recientes = [] 

kernel_apertura = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
kernel_cierre = np.ones((20, 20), np.uint8)

while True:
    ret, frame = cap.read()
    
    if not ret:
        break

    # Preprocesamiento de la imagen
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gris, (5, 5), 5)

    # Aplicar la mascara del sustractor y filtrar las sombras
    mascara = sustractor.apply(blur)
    _, mascara = cv2.threshold(mascara, 200, 255, cv2.THRESH_BINARY)

    #Operaciones morfologicas para limpiar ruido y unir vehiculos largos
    mascara_limpia = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel_apertura)
    mascara_limpia = cv2.morphologyEx(mascara_limpia, cv2.MORPH_CLOSE, kernel_cierre)

    #Encontrar los contornos de los objetos en movimiento
    contornos, _ = cv2.findContours(mascara_limpia, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #Dibujar la linea de conteo en la imagen original
    cv2.line(frame, (0, linea_conteo_y), (frame.shape[1], linea_conteo_y), (0, 255, 0), 2)

    #Lista para saber donde estan TODOS los autos en el frame actual
    centros_actuales = []

    for c in contornos:
        area = cv2.contourArea(c)

        # Ignorar areas pequeñas (ruido)
        if area < 600: 
            continue

        #Obtener las coordenadas del rectangulo delimitador y calcular centroide
        x, y, w, h = cv2.boundingRect(c)
        cx = x + int(w / 2)
        cy = y + int(h / 2)
        centroide = (cx, cy)
        
        centros_actuales.append(centroide)

        #Dibujar el rectangulo verde y el punto rojo
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame, centroide, 4, (0, 0, 255), -1)

        #Si la coordenada Y del centroide esta dentro del margen de la línea...
        if (linea_conteo_y - offset) < centroide[1] < (linea_conteo_y + offset):
            
            #Verificar si este auto ya fue contado recientemente
            ya_contado = False
            for auto in autos_recientes:
                distancia = math.sqrt((centroide[0] - auto[0])**2 + (centroide[1] - auto[1])**2)
                
                #Tolerancia amplia para vehículos rapidos o largos
                if distancia < 90: 
                    ya_contado = True
                    break
            
            #Si supero la prueba y es un auto nuevo, lo contamos y lo guardamos
            if not ya_contado:
                conteo_vehiculos += 1
                autos_recientes.append(centroide)
                #Cambiar la linea a rojo momentaneamente para indicar el conteo
                cv2.line(frame, (0, linea_conteo_y), (frame.shape[1], linea_conteo_y), (0, 0, 255), 2)

    # Revisamos los autos en memoria y actualizamos sus coordenadas para "seguirlos"
    autos_recientes_actualizados = []
    for auto in autos_recientes:
        for cx, cy in centros_actuales:
            distancia = math.sqrt((cx - auto[0])**2 + (cy - auto[1])**2)
            if distancia < 90:
                # Guardamos la posición NUEVA (cx, cy) para no perderle el rastro
                autos_recientes_actualizados.append((cx, cy))
                break 
    autos_recientes = autos_recientes_actualizados

    #Interfaz visual: Dibujar el cuadro negro y el texto del contador
    cv2.rectangle(frame, (30, 20), (350, 80), (0, 0, 0), -1)
    cv2.putText(frame, f"Vehiculos: {conteo_vehiculos}", (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Video Original', frame)

    if cv2.waitKey(30) & 0xFF == 27:
        break

#Liberar los recursos
cap.release()
cv2.destroyAllWindows()