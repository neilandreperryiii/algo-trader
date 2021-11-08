#%%

# imports
import os
import pandas as pd
from numpy import loadtxt
from keras.models import Sequential
from keras.layers import Dense

#%% md

# 1. Load Data

#%%

# define data url - text/csv file
dataUrl = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"

# request data 
df = pd.read_csv(dataUrl, header=None, encoding="utf-8")
df.head()

#%%

# convert dataframe to numpy matrix | https://www.pythonpool.com/numpy-read-csv/
dataset = df.values
dataset

#%%

# split data into input and output variables

# input variables (X)
X = dataset[:,0:8] # select the first 8 columns from index 0 to index 7 via the slice 0:8

# output variables (y)
y = dataset[:,8]

#%% md

# 2. Define Keras Model

#%%

# define the keras model
model = Sequential()
model.add(Dense(12, input_dim=8, activation='relu'))
model.add(Dense(8, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model

#%% md

# 3. Compile Keras Model

#%%

# compile the keras model
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

#%% md

# 4. Fit Keras Model

#%%

# fit the keras model on the dataset
model.fit(X, y, epochs=150, batch_size=10, verbose=0)

#%% md

# 5. Evaluate Keras Model

#%%

# evaluate the keras model
_, accuracy = model.evaluate(X, y, verbose=0)
print('Accuracy: %.2f' % (accuracy*100))

#%% md

# 6. Make Predictions

#%%

# make probability predictions with the model
# predictions = model.predict(X)
 
# make class predictions with the model - round predictions
predictions = (model.predict(X) > 0.5).astype(int)
predictions

#%% md

# 1. Summarize Predictions

#%%

# summarize the first 5 cases
for i in range(60):
	print('%s => %d (expected %d)' % (X[i].tolist(), predictions[i], y[i]))
