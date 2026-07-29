import cv2
from datetime import datetime
import time

cap = cv2.VideoCapture(0)

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 30

recording = False
writer = None
countdown_active = False
countdown_start = 0

while True:
    _, frame = cap.read()

    if recording:
        writer.write(frame)
        cv2.putText(frame, 'GRABANDO', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    if countdown_active:
        elapsed = time.time() - countdown_start
        remaining = max(0, 5 - int(elapsed))
        cv2.putText(frame, f'Foto en: {remaining}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if remaining == 0:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            cv2.imwrite(f'captura_{timestamp}.jpg', frame)
            print('Captura guardada')
            countdown_active = False

    # Instrucciones en pantalla
    cv2.putText(frame, 'R: grabar/detener', (10, frame_height - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, 'C: captura con delay | Q: salir', (10, frame_height - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow('mi primer OpenCv', frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    elif key == ord('r'):
        if not recording:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            writer = cv2.VideoWriter(f'grabacion_{timestamp}.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))
            recording = True
            print('Grabacion iniciada')
        else:
            recording = False
            writer.release()
            writer = None
            print('Grabacion guardada')

    elif key == ord('c'):
        if not countdown_active:
            countdown_active = True
            countdown_start = time.time()
            print('Captura en 5 segundos...')

cap.release()
cv2.destroyAllWindows()