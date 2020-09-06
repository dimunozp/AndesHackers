# -*- coding: utf-8 -*-
"""MedHacks.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1x7URmsjRoTrKaHdPvqHzGeUHZNgG2lMN

# Skin lesion classifier

## Libraries
"""

import numpy as np
import cv2
from keras.callbacks import ModelCheckpoint,EarlyStopping
from keras.layers import Conv2D, Flatten, MaxPooling2D,Dense,Dropout,SpatialDropout2D
from keras.models  import Sequential
from keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img, array_to_img
import random,os,glob
import matplotlib.pyplot as plt

"""## Dataset"""

!unzip Skins\ Lesions.zip

dir_path = "Skins Lesions"
img_list = glob.glob(os.path.join(dir_path))
#!rm -rf "Skins Lesions/benign"

"""## Data Division (Training - Testing)"""

train=ImageDataGenerator(horizontal_flip=True,
                         vertical_flip=True,
                         validation_split=0.1,
                         rescale=1./255,
                         shear_range = 0.1,
                         zoom_range = 0.1,
                         width_shift_range = 0.1,
                         height_shift_range = 0.1,)

test=ImageDataGenerator(rescale=1/255,
                        validation_split=0.1)

train_generator=train.flow_from_directory(dir_path,
                                          target_size=(450,450),
                                          batch_size=32,
                                          class_mode='categorical',
                                          subset='training')

test_generator=test.flow_from_directory(dir_path,
                                        target_size=(450,450),
                                        batch_size=32,
                                        class_mode='categorical',
                                        subset='validation')

labels = (train_generator.class_indices)
print(labels)

labels = dict((v,k) for k,v in labels.items())
print(labels)

for image_batch, label_batch in train_generator:
  break
image_batch.shape, label_batch.shape

"""## Classes File"""

print (train_generator.class_indices)

Labels = '\n'.join(sorted(train_generator.class_indices.keys()))

with open('labels.txt', 'w') as f:
  f.write(Labels)

"""## Model Definition"""

model=Sequential()

#Convolution
model.add(Conv2D(32,(3,3), padding='same',input_shape=(450,450,3),activation='relu'))
model.add(MaxPooling2D(pool_size=2)) 

model.add(Conv2D(64,(3,3), padding='same',activation='relu'))
model.add(MaxPooling2D(pool_size=2)) 

model.add(Conv2D(128,(3,3), padding='same',activation='relu'))
model.add(MaxPooling2D(pool_size=2)) 

#Clasificacion
model.add(Flatten())

model.add(Dense(64,activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(32,activation='relu'))

model.add(Dropout(0.2))
model.add(Dense(9,activation='softmax'))

filepath="trained_model.h5"
checkpoint1 = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
callbacks_list = [checkpoint1]

"""## Model Summary"""

model.summary()

"""## Cost function and optimization"""

model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['acc'])

"""## CNN Training"""

history = model.fit_generator(train_generator,
                              epochs=10,
                              steps_per_epoch=2124//20,
                              validation_data=test_generator,
                              validation_steps=233//20,
                              workers = 4,
                              callbacks=callbacks_list)

"""## Model Testing"""

from keras.preprocessing import image
import tensorflow as tf

img_path = "ack1.jpg"

img = image.load_img(img_path, target_size=(450, 450))
img = image.img_to_array(img, dtype=np.uint8)
img=np.array(img)/255.0
model = tf.keras.models.load_model("trained_model.h5")
plt.title("Image Selected")
plt.axis('off')
plt.imshow(img.squeeze())

p=model.predict(img[np.newaxis, ...])

print("Probability: ",np.max(p[0], axis=-1))
predicted_class = labels[np.argmax(p[0], axis=-1)]
print("Classification:",predicted_class)

classes=[]
prob=[]
print("Classes Probabilities")

for i,j in enumerate (p[0],0):
    print(labels[i].upper(),':',round(j*100,2),'%')
    classes.append(labels[i])
    prob.append(round(j*100,2))
    
def plot_bar_x():
    # this is for plotting purpose
    index = np.arange(len(classes))
    plt.bar(index, prob)
    plt.xlabel('Types', fontsize=12)
    plt.ylabel('Probability', fontsize=12)
    plt.xticks(index, classes, fontsize=12, rotation=20)
    plt.title('Loading Image Analysis')
    plt.show()
plot_bar_x()

"""## Accuracy vs Number of epochs"""

acc = history.history['acc']
val_acc = history.history['val_acc']

plt.figure(figsize=(8, 8))
plt.subplot(2, 1, 1)
plt.plot(acc, label='Accuracy of training')
plt.plot(val_acc, label='Validation')
plt.legend(loc='lower right')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.ylim([min(plt.ylim()),1])
plt.title('Accuracy of training')

"""## Loss vs Number of epochs"""

loss = history.history['loss']
val_loss = history.history['val_loss']

plt.subplot(2, 1, 2)
plt.plot(loss, label='Loss of training')
plt.plot(val_loss, label='Validacion')
plt.legend(loc='upper right')
plt.xlabel('Epochs')
plt.ylabel('Cross Entropy')
plt.ylim([0,max(plt.ylim())])
plt.title('Loss of training')
plt.show()

"""## Keras to TensorFlow Lite"""

import tensorflow as tf

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the TF Lite model.
with tf.io.gfile.GFile('trained_model.tflite', 'wb') as f:
  f.write(tflite_model)



"""## User Interface"""

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import tkinter as tk
from PIL import Image, ImageTk
import glob

import os
import cv2
import tensorflow as tf
import numpy as np
from keras.preprocessing import image
import matplotlib.pyplot as plt

def predict(img_path):
    labels = {0: 'actinic keratosis', 1: 'basal cell carcinoma', 2: 'dermatofibroma', 3: 'melanoma', 4: 'nevus', 5: 'pigmented benign keratosis', 6: 'seborrheic keratosis', 7: 'squamous cell carcinoma', 8: 'vascular lesion'}
    mensaje=""
    # Cargo la imagen que voy a predecir
    img = image.load_img(img_path, target_size=(300, 300))
    img = image.img_to_array(img, dtype=np.uint8)
    img = np.array(img) / 255.0

    # cargo el modelo para que realice las predicciones
    model = tf.keras.models.load_model("trained_model100.h5")
    p = model.predict(img[np.newaxis, ...])
    pro = np.max(p[0], axis=-1)

    # Tipos de desechos
    predicted_class = labels[np.argmax(p[0], axis=-1)]

    mensaje += "Pertenece a la clase "+ predicted_class + "\n"


    #img = image.load_img(img_path, target_size=(300, 300))
    #img = image.img_to_array(img, dtype=np.uint8)
    #img = np.array(img) / 255.0

    plt.title("Imagen selecionada")
    plt.axis('off')
    plt.imshow(img.squeeze())

    #p = model.predict(img[np.newaxis, ...])

    mensaje+="Con una probabilidad de: " + str(np.max(p[0],axis=-1)) + "\n"

    #predijo = img_path.split("/")[-2]
    #if (predijo == predicted_class):
    #    mensaje += "¡Predicción exitosa!"
    #else:
    #    mensaje += "Predicción fallida..."
    return mensaje

class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Clasificador de basura")
        self.minsize(640, 400)

        self.labelFrame = ttk.LabelFrame(self, text="Escoger imagen ")
        self.labelFrame.grid(column=0, row=1, padx=20, pady=20)

        self.button()

    def button(self):
        self.button = ttk.Button(self.labelFrame, text="Examinar imagen", command=self.fileDialog)
        self.button.grid(column=1, row=1)

    def fileDialog(self):
        self.filename = filedialog.askopenfilename(initialdir="/", title="Select A File")

        jpeg = glob.glob(self.filename)[0];
        im = Image.open(jpeg)
        im.thumbnail((192, 340), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(im)
        label = tk.Label(root, image=photo)

        label.img = photo

        label.grid(column=1, row=3)
        prediccion=predict(
            img_path=self.filename)
        label2 = ttk.Label(text=prediccion)
        label2.grid(column=1, row=4)


root = Root()
root.mainloop()