import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import tkinter as tk
from tkinter import*
import PIL
from PIL import ImageTk, Image

##############################################
## Authors:                                 ##
## M.Sc. Hector E. Ugarte R.                ##
## M.Sc. Boris Chullo L.                    ##
##############################################

#Using tkinter to create visual forms
root = tk.Tk()
root.config(width=1200, height=600)
root.title("▮ Football field condition classifier prototype based on K-means clustering ▨")

#Number of cluster, for k-means algorithm
clusters = 6
#polygons points
list_of_points = []
created = False

#function that determines if a colour is considered green (shades of green)
def isGreen(x):
    greenImg = cv2.imread("allgreens.png")
    #removing black pixels from mask
    greenImg = greenImg[np.any(greenImg!=0,axis=-1)]
    return(x == greenImg).all(1).any()

img = cv2.imread("")
imgaux = cv2.imread("")

#Frame for presenting found colours
frame1 = tk.Frame(root, bg='#C0C0C0', bd=1.5)
frame1.place(x=20, y=450, height=100, width=400)

#Frame for presenting most dominant colours
frame2 = tk.Frame(root, bg='#C0C0C0', bd=1.5)
frame2.place(x=450, y=450, height=100, width=730)

#Frame for visualizing the image
frame3 = tk.Frame(root, bg='#C0C0C0', bd=1.5)
frame3.place(x=450, y=30, height=400, width=730)

#Frame for buttons and resulting text
frame4 = tk.Frame(root, bg='#C0C0C0', bd=1.5)
frame4.place(x=20, y=30, height=400, width=400)

#main canvas where image is loaded and polygon is draw
mainCanvas = tk.Canvas(frame3, height=400, width=730, bg='white')
mainCanvas.pack()
mainCanvas.place(relx = 0.0, rely = 1.0, anchor ='sw')

#event for left button mouse
def leftClick( event ):
    global list_of_points
    global tText
    global created
    global line

    if(created == False):
        tText.insert(tk.INSERT,"Point: ("+str(event.x)+","+str(event.y)+") ")
        list_of_points.append([event.x, event.y])
        if(len(list_of_points) > 1):
            line = mainCanvas.create_line(list_of_points[len(list_of_points)-2][0],list_of_points[len(list_of_points)-2][1],list_of_points[len(list_of_points)-1][0],list_of_points[len(list_of_points)-1][1],width=4, fill='red')

#event for double button mouse
def doubleClick( event ):
    global img
    global polygon
    global list_of_points
    global tText
    global created
    global bProcess
    global bSelect

    if(created == False):
        polygon = mainCanvas.create_polygon(list_of_points, fill='', outline='red', width=4)
        tText.insert(tk.INSERT,"\nPolygon created!\n")
        tText.insert(tk.INSERT,"Now you can perform k-means!\n")
        mask = np.zeros(img.shape, dtype=np.uint8)
        channel_count = img.shape[2]
        ignore_mask_color = (255,)*channel_count
        cv2.fillPoly(mask,np.array([list_of_points],dtype=np.int32), ignore_mask_color)
        img = cv2.bitwise_and(img,mask)

    #removing black pixels from mask
    img = img[np.any(img!=0,axis=-1)]
    created = True

    bProcess.config(state="normal")
    bSelect.config(state="disabled")

#event for right button mouse
def rightClick( event ):
    global tText
    global img
    global created
    global bProcess
    
    mainCanvas.delete(polygon)
    mainCanvas.delete("all")
    mainCanvas.create_image(0,0,image=imag,anchor="nw")
    list_of_points.clear()
    created=False
    img = imgaux
    tText.delete(1.0,END)
    tText.insert(tk.INSERT,"Polygon removed!\nYou have to draw a new polygon using the mouse\n")
    bProcess.config(state="disabled")

#function to load image on canvas
def loadImage():
    global imag
    global img
    global imgaux
    global list_of_points
    global tText
    filename = filedialog.askopenfilename(filetypes = (("image files", "*.png;*.jpg")
                                                             ,("All files", "*.*") ))
    img = cv2.imread(filename)
    img = cv2.resize(img, (730,400), interpolation = cv2.INTER_AREA)
    imgaux = img
    im = cv2.imread(filename)
    imag = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    imag = ImageTk.PhotoImage(image=Image.fromarray(imag).resize((730, 400), Image.ANTIALIAS))
    
    mainCanvas.create_image(0,0,image=imag,anchor="nw")
    mainCanvas.bind( "<Button>", leftClick )
    mainCanvas.bind("<Double-Button>", doubleClick )
    mainCanvas.bind("<Button-3>", rightClick)

    tText = tk.Text(frame4,height = 20, width = 49)
    tText.insert(tk.INSERT,"First draw a polygon with the mouse where the field is: \n")
    tText.place(x=0, y=63)

#converting rgb format to hex for using with tkinter
def rgbtohex(r,g,b):
    return f'#{r:02x}{g:02x}{b:02x}'

#main function
def process():
    global tText
    global bSelect
    global bProcess
    #Sharpening image
    kernel = np.array([[0, -1, 0],
                       [-1, 5,-1],
                       [0, -1, 0]])
    image_sharp = cv2.filter2D(src=img, ddepth=-1, kernel=kernel)

    flat_img = np.reshape(image_sharp,(-1,3))

    kmeans = KMeans(n_clusters=clusters,random_state=0)
    kmeans.fit(flat_img)

    dominant_colours = np.array(kmeans.cluster_centers_,dtype='uint')
    proportions = (np.unique(kmeans.labels_,return_counts=True)[1])/flat_img.shape[0]

    #Zipping dominant_colours and proportions iterables in one
    proportions_dominants = zip(proportions,dominant_colours)
    #Sorting from highest to lowest
    proportions_dominants = sorted(proportions_dominants,reverse=True)

    #Canvas for found colours using k-means
    canvasColours = tk.Canvas(frame1, height=100, width=400, bg='white')
    a = 0
    for i in range(clusters):       
        arc = canvasColours.create_oval(5+a, 27, 65+a, 87, width=1, fill=rgbtohex(dominant_colours[i][2],dominant_colours[i][1],dominant_colours[i][0]))
        a=a+65
    canvasColours.create_text(195, 15, font=("Purisa", 14), text='Found colours using k-means')
    canvasColours.pack()
    canvasColours.place(relx = 0.0, rely = 1.0, anchor ='sw')

    #Canvas for dominant colours proportion found using k-means    
    canvasProportions = tk.Canvas(frame2, height=100, width=730, bg='white')
    b = 0
    c = 0
    for i in range(clusters):
        b=b+round(proportions_dominants[i][0]*730)
        arc = canvasProportions.create_rectangle(0+c, 0, b, 70, width=1, fill=rgbtohex(proportions_dominants[i][1][2],proportions_dominants[i][1][1],proportions_dominants[i][1][0]))
        c=c+round(proportions_dominants[i][0]*730)
    canvasProportions.create_text(350, 85, font=("Purisa", 14), text='Dominant colours proportion found using k-means')
    canvasProportions.pack()
    canvasProportions.place(relx = 0.0, rely = 1.0, anchor ='sw')

    listText = ["FIRST COLOUR","SECOND COLOUR","THIRD COLOUR","FOURTH COLOUR", "FIFTH COLOUR", "SIXTH COLOUR"]
    
    bSelect.config(state="normal")
    bProcess.config(state="disabled")

    tText.tag_config('positive_result', background="yellow", foreground="blue", font=("Georgia", "12", "bold"))
    tText.tag_config('negative_result', background="yellow", foreground="red", font=("Georgia", "12", "bold"))
    
    totalPercentage=0.0
    for j in range(len(proportions_dominants)):
        tText.insert(tk.END,listText[j]+" PROPORTION: "+ str(round(proportions_dominants[j][0],2)) +" IS GREEN?: "+ str(isGreen([proportions_dominants[j][1][2],proportions_dominants[j][1][1],proportions_dominants[j][1][0]]))+"\n")
        if(isGreen([proportions_dominants[j][1][2],proportions_dominants[j][1][1],proportions_dominants[j][1][0]])):
           totalPercentage= totalPercentage+float(proportions_dominants[j][0])
    tText.insert(tk.END,"\nTotal percentage of shadows of green: \n"+str(round(totalPercentage,2))+"\n")
    if(totalPercentage < 0.8):
        tText.insert(tk.END,"*** THE PITCH CONDITION IS BAD",'negative_result')
    else:
        tText.insert(tk.END,"*** THE PITCH CONDITION IS GOOD",'positive_result')

#Button to choose image
bSelect = tk.Button(frame4, text="Choose an image:", command=loadImage)
bSelect.place(x=0, y=0)

#Button to process image
bProcess = tk.Button(frame4, text="Perform K-means:", command=process, state="disabled")
bProcess.place(x=0, y=30)

root.mainloop()
