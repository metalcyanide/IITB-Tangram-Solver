import numpy as np 
import cv2 
from matplotlib import pyplot as plt


def pshow(img):
    if (img.ndim > 2):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.figure()
    plt.imshow(img)
    plt.show()


plt.ion()
img_location = './database/test.png'

font = cv2.FONT_HERSHEY_COMPLEX 
img = cv2.imread(img_location, cv2.IMREAD_GRAYSCALE) 
img2 = cv2.imread(img_location, cv2.IMREAD_COLOR) 

_, threshold = cv2.threshold(img, 110, 255, cv2.THRESH_BINARY) 


# threshold = threshold / 255
# inv_thr = 1 - threshold
# kernel3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
# erosion = cv2.morphologyEx(inv_thr, cv2.MORPH_ERODE, kernel3)
# threshold = ((1 - erosion)*255).astype('uint8')

canny = cv2.Canny(img2, 120, 255, apertureSize=7, L2gradient=True)

pshow(canny)

contours, _= cv2.findContours(canny, cv2.RETR_TREE, 
							cv2.CHAIN_APPROX_SIMPLE) 

for cnt in contours : 

	approx = cv2.approxPolyDP(cnt, 0.007 * cv2.arcLength(cnt, True), True) 
	cv2.drawContours(img2, [approx], 0, (0, 0, 255), 5) 
	n = approx.ravel() 
	i = 0

	for j in n : 
		if(i % 2 == 0): 
			x = n[i] 
			y = n[i + 1] 

			string = str(x) + " " + str(y) 

			if(i == 0): #finding top most of the tan piece
				cv2.putText(img2, "Arrow tip", (x, y), 
								font, 0.5, (255, 0, 0)) 
			else: 
				# text on remaining co-ordinates. 
				cv2.putText(img2, string, (x, y), 
						font, 0.5, (0, 255, 0)) 
		i = i + 1

fig,ax = plt.subplots()
plt.subplot(121),plt.imshow(img)
plt.title('Original Image'),
plt.subplot(122),plt.imshow(img2)
plt.title('filtered Image'),
plt.show()

input("press enter to exit (irony)")