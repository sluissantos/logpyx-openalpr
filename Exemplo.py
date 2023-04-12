import cv2
import pytesseract
import numpy as np

def encontrarRoiPlaca(source):
    t_lower = 1
    t_upper = 299
    aperture_size = 5
    im = cv2.imread(source)
    norm = np.zeros((800,800))
    img = cv2.normalize(im,norm,0,255,cv2.NORM_MINMAX)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("cinza", img)
    
    _, bin = cv2.threshold(cinza, 130, 255, cv2.THRESH_BINARY)
    cv2.imshow("binary", bin)

    dist_transform = cv2.distanceTransform(bin, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    

    
    #cinza = cv2.cvtColor(dist_transform, cv2.COLOR_BGR2GRAY)
    
    #cv2.imshow("cinza", cinza)
    
    #_, bin1 = cv2.threshold(dist_transform, 130, 255, cv2.THRESH_BINARY)
    
    #contornos, hierarquia = cv2.findContours(bin1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    
    #cv2.drawContours(img, contornos, -1, (0, 255, 0), 1) 
    
    #cv2.imshow('Imagem normalizada', dist_transform) 
    
    #edge = cv2.Canny(dist_transform, t_lower, t_upper, apertureSize=aperture_size)
    #cv2.imshow('edge', edge)

    #desfoque = cv2.GaussianBlur(edge, (5, 5), 0)
    
    contornos, hierarquia = cv2.findContours(bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    #cv2.drawContours(img, contornos, -1, (0, 255, 0), 1)

    for c in contornos:
        perimetro = cv2.arcLength(c, True)
        if perimetro > 120:
            aprox = cv2.approxPolyDP(c, 0.03 * perimetro, True)
            if len(aprox) == 4:
                (x, y, alt, lar) = cv2.boundingRect(c)
                cv2.rectangle(img, (x, y), (x + alt, y + lar), (0, 255, 0), 2)
                roi = img[y:y + lar, x:x + alt]
                cv2.imwrite('output/roi.png', roi)

    cv2.imshow("contornos", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def preProcessamentoRoiPlaca():
    img_roi = cv2.imread("output/roi.png")

    if img_roi is None:
        return

    resize_img_roi = cv2.resize(img_roi, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)

    # Converte para escala de cinza
    img_cinza = cv2.cvtColor(resize_img_roi, cv2.COLOR_BGR2GRAY)

    # Binariza imagem
    _, img_binary = cv2.threshold(img_cinza, 130, 255, cv2.THRESH_BINARY)

    
    # Desfoque na Imagem
    img_desfoque = cv2.GaussianBlur(img_binary, (5, 5), 0)

    # Grava o pre-processamento para o OCR
    cv2.imwrite("output/roi-ocr.png", img_desfoque)

    #cv2.imshow("ROI", img_desfoque)
    
    cv2.waitKey(0)

    return img_desfoque


def ocrImageRoiPlaca():
    image = cv2.imread("output/roi-ocr.png")

    config = r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --psm 6'

    saida = pytesseract.image_to_string(image, lang='eng', config=config)

    return saida


if __name__ == "__main__":
    encontrarRoiPlaca("resource/carro.jpeg")

    pre = preProcessamentoRoiPlaca()

    ocr = ocrImageRoiPlaca()

    print(ocr)
