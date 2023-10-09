import os
import cv2
import pytesseract
import numpy as np
import platform
import queue
import time
import threading
from openalpr import Alpr
import mqtt_interface as mqtt_init

# Define para cada posição dos caracteres da placa, o caractere mais encontrado nas leitura.
class MostCommonChar():
    lastFinalPlate = None
    def __init__(self):
        self.char0 = {}
        self.char1 = {}
        self.char2 = {}
        self.char3 = {}
        self.char4 = {}
        self.char5 = {}
        self.char6 = {}
        return

    def insertChar(self, plate):
        for i in range(len(plate)):
            if i == 0:
                if plate[i] in self.char0:
                    self.char0[plate[i]] += 1
                else:
                    self.char0[plate[i]] = 1
            if i == 1:
                if plate[i] in self.char1:
                    self.char1[plate[i]] += 1
                else:
                    self.char1[plate[i]] = 1
            if i == 2:
                if plate[i] in self.char2:
                    self.char2[plate[i]] += 1
                else:
                    self.char2[plate[i]] = 1
            if i == 3:
                if plate[i] in self.char3:
                    self.char3[plate[i]] += 1
                else:
                    self.char3[plate[i]] = 1
            if i == 4:
                if plate[i] in self.char4:
                    self.char4[plate[i]] += 1
                else:
                    self.char4[plate[i]] = 1
            if i == 5:
                if plate[i] in self.char5:
                    self.char5[plate[i]] += 1
                else:
                    self.char5[plate[i]] = 1
            if i == 6:
                if plate[i] in self.char6:
                    self.char6[plate[i]] += 1
                else:
                    self.char6[plate[i]] = 1
        return

    def getMostCommonPlate(self):
        c0 = max(self.char0, key=self.char0.get)
        c1 = max(self.char1, key=self.char1.get)
        c2 = max(self.char2, key=self.char2.get)
        c3 = max(self.char3, key=self.char3.get)
        c4 = max(self.char4, key=self.char4.get)
        c5 = max(self.char5, key=self.char5.get)
        c6 = max(self.char6, key=self.char6.get)
        finalPlate = c0+c1+c2+c3+c4+c5+c6
        if(self.lastFinalPlate == finalPlate):
            return None
        self.lastFinalPlate = finalPlate
        return finalPlate
    
    def cleanPlate(self):
        self.char0 = {}
        self.char1 = {}
        self.char2 = {}
        self.char3 = {}
        self.char4 = {}
        self.char5 = {}
        self.char6 = {}
        return
    
    def getChar(self):
        if any(self.char0):
            return 1
        return 0

# Redimenciona a imagem encontrada atraves do Cascade, normaliza, converte para cinza, binariza e desfoca. Função usada para tratar imagem de entrada para o Tesseract. 
def preProcessamentoRoi(img_roi):
    # redmensiona a imagem da placa em 4x
    img = cv2.resize(img_roi, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    norm = np.zeros((800,800))
    norm_image = cv2.normalize(img,norm,0,255,cv2.NORM_MINMAX)
    # Converte para escala de cinza
    img = cv2.cvtColor(norm_image, cv2.COLOR_BGR2GRAY)
    # Binariza imagem
    _, img = cv2.threshold(img, int(tesseract_gray), 255, cv2.THRESH_BINARY)
    # Desfoque na Imagem
    img = cv2.GaussianBlur(img, (5, 5), 0)
    return img

# Funcão para leitura e então armazenamento do frame no buffer da Fila.
def Receive(source):
    global terminate_threads
    cap = cv2.VideoCapture(source)
    while terminate_threads:
        ret, frame = cap.read()
        if not ret:
            cap.release()
            cap = reconnect(source)
            continue
        q.put(frame)

# Uso do Cascade.
def findRectPlateCascade(id, car_cascade):
    global tempo
    global flagContarTempo
    global platesALPR
    global platesOCR
    global finalPlate
    global terminate_threads
    global p1

    while terminate_threads:
        tempo = int(time.time())
        if not q.empty():
            frame = q.get()
            area = frame[int(min_line_frame):int(max_line_frane),:]# variáveis para limitar a "altura" do frame de entrada.
            area_printed = area
            cv2.imshow("area", area)
            norm = np.zeros((800,800))
            norm_image = cv2.normalize(area,norm,0,255,cv2.NORM_MINMAX)
            gray = cv2.cvtColor(norm_image, cv2.COLOR_BGR2GRAY)# tratamentos iniciais para uso do Cascade
            cars = car_cascade.detectMultiScale(gray, float(scale_factor_cascade), 1, minSize = (5,5), maxSize = (500,500))
            if len(cars) != 0:
                if((len(platesALPR)+len(platesOCR))>100):
                    print('Plates encontrados por ALPR = {} resultados.\n'.format(len(platesALPR)), end='')
                    print('Plates encontrados por OCR = {} resultados.\n'.format(len(platesOCR)), end='')
                    plate = finalPlate.getMostCommonPlate()
                    print('PLACA FINAL = ', plate)
                    mqtt_init.publish_plate(id, plate)
                    finalPlate.cleanPlate()          
                    tempo = 0.0
                    platesALPR = []
                    platesOCR = []
                    cars = []
                    terminate_threads = False
                    while not q.empty():
                        q.get()
                    p1.join()
                    print('tempo total = ', (int(time.time())-tempo))
                    time.sleep(10)
                    terminate_threads = True
                    p1 = threading.Thread(target=Receive, args=(camera_source,))
                    p1.start()

                else:
                    for (x, y, w, h) in cars:
                        area_printed = area
                        rect_plate = area[y:y + h, x:x + w]
                        plate_alpr = area[y:y + h, x:x + w]
                        reconhecimentoALPR(plate_alpr)# para as coordenadas encontradas, usar a biblioteca ALPR para detecção da placa.
                        reconhecimentoOCR(preProcessamentoRoi(plate_alpr))# para as coordenadas encontradas, usar o Tesseract para detecção da placa.
                        cv2.rectangle(area_printed, (x, y), (x + w, y + h), (0, 0, 255), 1)
                        encontrarRoiPlaca(rect_plate)
                        cv2.imshow('area_printed', area_printed)
                        tempo = 0
                        flagContarTempo = 0
                        break
            else:
                if(flagContarTempo == 0):
                    flagContarTempo = 1
                    tempo = int(time.time())
                if(flagContarTempo == 1):
                    if(int(time.time()) - tempo >= int(time_out_send_plate)):# timeout da detecção. 
                        if(len(platesALPR)>int(max_plates)):
                            print('maior que 1000')
                        if(finalPlate.getChar()):
                            print('Plates encontrados por ALPR = {} resultados.\n'.format(len(platesALPR)), end='')
                            print('Plates encontrados por OCR = {} resultados.\n'.format(len(platesOCR)), end='')
                            plate = finalPlate.getMostCommonPlate()
                            print('PLACA FINAL = ', plate)
                            mqtt_init.publish_plate(id, plate)
                            finalPlate.cleanPlate()          
                            tempo = 0.0
                            platesALPR = []
                            platesOCR = []

        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return

# Função recursiva para o caso em que a câmera IP tenha falha de conexão.
def reconnect(source): 
    global status
    while True:
        print("Trying to reconnect camera...")
        cap = cv2.VideoCapture(source)
        status = False
        if cap.isOpened():
            print("Camera reconnected!")
            status = True
            return cap
        time.sleep(1)

# Tratamento da imagem encontrada pelo Cascade. Uso de técnica de detecção de contorno para obter o placa.
def encontrarRoiPlaca(rect_plate):
    img = rect_plate
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bin = cv2.threshold(cinza, int(tesseract_gray), 255, cv2.THRESH_BINARY)
    contours, hier = cv2.findContours(bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    bin = cv2.resize(bin, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC)
    for c in contours:
        perimetro = cv2.arcLength(c, True)
        if perimetro > 120 and perimetro < 400: # Definição do perímetro mínimo e máximo dos contornos encontrados para minorar os falsos positivos.
            aprox = cv2.approxPolyDP(c, 0.03 * perimetro, True)
            if len(aprox) == 4:
                (x1, y1, w1, h1) = cv2.boundingRect(c)
                cv2.rectangle(rect_plate, (x1, y1), ((x1 + w1) , (y1 + h1)), (0, 255, 0), 1)
                roi = rect_plate[y1:(y1 + h1), x1:(x1 + w1)]
                reconhecimentoOCR(preProcessamentoRoi(roi))
    return
    
# Função Tesseract. 
def reconhecimentoOCR(plate):
    config = r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm 6'
    text = list(pytesseract.image_to_string(plate, lang='eng', config=config))
    if(len(text)==lenPlate):
        if(normCaracterPlateList(text)[0] == 1):
            platesOCR.append(normCaracterPlateList(text[0:7])[1])
            print('Tesseract= ', normCaracterPlateList(text[0:7])[1])
            finalPlate.insertChar(normCaracterPlateList(text[0:7])[1])

    return 
    
# Realiza as possíveis correções para cada posição de entrada dos caracteres. Se aparecer número onde é letra, define o valor provável, e vice-versa.
def normCaracterPlateList(text):
    aux = None
    for i in range(len(text)):
        if(i>=0 and i<=2):
            if(text[i] == '8'):
                text[i] == 'B'
            elif(text[i] == '6'):
                text[i] == 'G'
            elif(text[i] == '1'):
                text[i] == 'I'
            elif(text[i] == '0'):
                text[i] = 'O'
            elif(text[i] == '2'):
                text[i] = 'Z'
            if(int(ord(text[i]))<65 or int(ord(text[i]))>90):
                return 0, aux
        if(i==3 or i==5 or i==6):
            if(text[i] == 'B'):
                text[i] == '8'
            elif(text[i] == 'G'):
                text[i] == '6'
            elif(text[i] == 'I'):
                text[i] == '1'
            elif(text[i] == 'O'):
                text[i] = '0'
            elif(text[i] == 'Z'):
                text[i] = '2'
            if(int(ord(text[i]))<48 or int(ord(text[i]))>57):
                return 0, aux
    aux = ''.join(text)
    return 1, aux

# Função ALPR.
def reconhecimentoALPR(plate_alpr):
    try:
        alpr = Alpr('br', '/home/logpyx-openalpr/config/openalpr.defaults.conf', '/home/logpyx-openalpr/runtime_data')# parâmetros obrigatórios para chamamento da função ALPR.
        if not alpr.is_loaded():
            print("Error loading OpenALPR")
        else:
            alpr.set_top_n(7)
            alpr.set_detect_region(False)
            retval, buffer = cv2.imencode('.jpg', plate_alpr)
            jpeg_bytes = bytes(buffer)
            results = alpr.recognize_array(jpeg_bytes)
            for plate in results['results']:
                for candidate in plate['candidates']:
                    aux = list(candidate['plate'])
                    if(normCaracterPlateList(aux)[0] == 1):
                        print('OpenALPR = ', ''.join(aux))
                        platesALPR.append(''.join(aux))
                        finalPlate.insertChar(''.join(aux))

    finally:
        if alpr:
            alpr.unload()
    return

def publish_periodically(id):
    global status
    while True:
        mqtt_init.publish_status(id, status)
        time.sleep(30)  # Aguarda 30 segundos

def check_mqtt_connection():
    while True:
        mqtt_init.reconnect()
#Init
if __name__ == "__main__":
    q=queue.Queue()

    terminate_threads = True
    status = True

    # variáveis globais atribúidas a partir das variáveis de ambiente inicializadas no sistema.

    tesseract_gray = "130"
    scale_factor_cascade = "1.7"
    camera_source = "rtsp://admin:128Parsecs!@10.50.239.20/Streaming/channels/101"
    time_out_send_plate = "5"
    min_line_frame = '200'
    max_line_frane = '900'
    max_plates = '1000'
    '''
    tesseract_gray = os.getenv("TESSERACT_GRAY")
    scale_factor_cascade = os.getenv("SCALE_FACTOR_CASCADE")
    camera_source = os.getenv("CAMERA_SOURCE")
    time_out_send_plate = os.getenv("TIME_OUT_SEND_PLATE")
    min_line_frame = os.getenv("MIN_LINE_FRAME")
    max_line_frane = os.getenv("MAX_LINE_FRAME")
    max_plate = os.getenv("MAX_PLATES")
    '''
    print('\ngray=', tesseract_gray)
    print('scale=', scale_factor_cascade)
    print('camerasource=', camera_source)
    print('time=', time_out_send_plate)
    print('minLine=', min_line_frame)
    print('maxLine=', max_line_frane)
    
    finalPlate = MostCommonChar()
    platesALPR = []
    platesOCR = []
    lenPlate = None
    tempo = None
    flagContarTempo = None

    ident = camera_source.split("@")[1]

    plat = platform.system()
    if(plat == 'Linux'):
        lenPlate = 9
    elif(plat == 'Windows'):
        lenPlate = 8
    car_cascade = cv2.CascadeClassifier('/home/logpyx-openalpr/runtime_data/region/br.xml')

    # definição e start das threads
    p0 = threading.Thread(target=check_mqtt_connection)
    p1 = threading.Thread(target=Receive, args=(camera_source,))
    p2 = threading.Thread(target=findRectPlateCascade, args=(ident, car_cascade))
    p3 = threading.Thread(target=publish_periodically, args=(ident,))

    p0.start()
    p1.start()
    p2.start()
    p3.start()
