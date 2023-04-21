import cv2
import pytesseract
import numpy as np
import platform
from send_to_cloud import Send_to_cloud_Mqtt
import queue
import time
import threading
from openalpr import Alpr
import paho.mqtt.client as mqttClient

q=queue.Queue()

class MostCommonChar():
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

def preProcessamentoRoi(img_roi):
    # redmensiona a imagem da placa em 4x
    img = cv2.resize(img_roi, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    norm = np.zeros((800,800))
    norm_image = cv2.normalize(img,norm,0,255,cv2.NORM_MINMAX)
    # Converte para escala de cinza
    img = cv2.cvtColor(norm_image, cv2.COLOR_BGR2GRAY)
    # Binariza imagem
    _, img = cv2.threshold(img, 130, 255, cv2.THRESH_BINARY)
    # Desfoque na Imagem
    img = cv2.GaussianBlur(img, (5, 5), 0)
    return img

def Receive(source):
    cap = cv2.VideoCapture(source)
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.release()
            cap = reconnect(source)
            continue
        q.put(frame)

def findRectPlateCascade(car_cascade):
    while True:
        if not q.empty():
            frame = q.get()
            area = frame[100:900, :]
            cv2.imshow('frame', frame)
            area_printed = area
            norm = np.zeros((800,800))
            norm_image = cv2.normalize(area,norm,0,255,cv2.NORM_MINMAX)
            gray = cv2.cvtColor(norm_image, cv2.COLOR_BGR2GRAY)
            cars = car_cascade.detectMultiScale(gray, 1.7, 1, minSize = (5,5), maxSize = (500,500))
            if len(cars) != 0:
                for (x, y, w, h) in cars:
                    area_printed = area
                    rect_plate = area[y:y + h, x:x + w]
                    plate_alpr = area[y:y + h, x:x + w]
                    reconhecimentoALPR(plate_alpr)
                    reconhecimentoOCR(preProcessamentoRoi(plate_alpr))
                    cv2.rectangle(area_printed, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    encontrarRoiPlaca(rect_plate)
                    cv2.imshow('area_printed', area_printed)
                    global tempo
                    tempo = 0
                    global flagContarTempo
                    flagContarTempo = 1
                    flagContarTempo = 0
                    break
            else:
                if(flagContarTempo == 0):
                    flagContarTempo = 1
                    tempo = int(time.time())
                if(flagContarTempo == 1):
                    if(int(time.time()) - tempo >= 5):
                        if(finalPlate.getChar()):
                            print('Plates encontrados por ALPR = {} resultados.\n'.format(len(platesALPR)), end='')
                            print('Plates encontrados por OCR = {} resultados.\n'.format(len(platesOCR)), end='')
                            print('PLACA FINAL = ', finalPlate.getMostCommonPlate())
                            send_data_to_cloud.send_message_to_cloud(send_data_to_cloud.client, finalPlate.getMostCommonPlate())
                            finalPlate.cleanPlate()          

        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return

tempo = 0.0

def reconnect(source):
    while True:
        print("Trying to reconnect...")
        cap = cv2.VideoCapture(source)
        if cap.isOpened():
            print("Reconnected!")
            return cap
        time.sleep(1)

def encontrarRoiPlaca(rect_plate):
    img = rect_plate
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bin = cv2.threshold(cinza, 130, 255, cv2.THRESH_BINARY)
    contours, hier = cv2.findContours(bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    bin = cv2.resize(bin, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC)
    for c in contours:
        perimetro = cv2.arcLength(c, True)
        if perimetro > 120 and perimetro < 400:
            aprox = cv2.approxPolyDP(c, 0.03 * perimetro, True)
            if len(aprox) == 4:
                (x1, y1, w1, h1) = cv2.boundingRect(c)
                cv2.rectangle(rect_plate, (x1, y1), ((x1 + w1) , (y1 + h1)), (0, 255, 0), 1)
                roi = rect_plate[y1:(y1 + h1), x1:(x1 + w1)]
                reconhecimentoOCR(preProcessamentoRoi(roi))
    return
    
def reconhecimentoOCR(plate):
    config = r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm 6'
    text = list(pytesseract.image_to_string(plate, lang='eng', config=config))
    if(len(text)==lenPlate):
        if(normCaracterPlateList(text)[0] == 1):
            platesOCR.append(normCaracterPlateList(text[0:7])[1])
            print('Tesseract= ', normCaracterPlateList(text[0:7])[1])
            finalPlate.insertChar(normCaracterPlateList(text[0:7])[1])

    return 
    
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

def reconhecimentoALPR(plate_alpr):
    try:
        alpr = Alpr('br', '/usr/share/openalpr/config/openalpr.defaults.conf', '/usr/share/openalpr/runtime_data')
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


if __name__ == "__main__":
    send_data_to_cloud = Send_to_cloud_Mqtt()
    user = "gwqa.revolog.com.br"
    password = "128Parsecs!"
    client = mqttClient.Client("Python")
    client.username_pw_set(user, password=password)
    finalPlate = MostCommonChar()
    platesALPR = []
    platesOCR = []
    lenPlate = 0
    tempo = None
    flagContarTempo = None
    plat = platform.system()
    if(plat == 'Linux'):
        lenPlate = 9
    elif(plat == 'Windows'):
        lenPlate = 8
    source = "rtsp://admin:128Parsecs!@192.168.15.85/Streaming/channels/101"
    #source = '/dev/video0'
    #source = 'resource/carro1.mp4'
    car_cascade = cv2.CascadeClassifier('/usr/share/openalpr/runtime_data/region/br.xml')
    p1 = threading.Thread(target=Receive, args=(source,))
    p2 = threading.Thread(target=findRectPlateCascade, args=(car_cascade,))
    p1.start()
    p2.start()