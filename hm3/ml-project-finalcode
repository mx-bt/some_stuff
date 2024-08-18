"""HM3 SS23 ML Project"""
# Streamlit
import streamlit as st # to create the website with streamlit library

# Data processing and metrics
from sklearn.model_selection import train_test_split # to split the data into a training and testing fraction
from sklearn.preprocessing import StandardScaler
import pandas as pd # Data format and analytics library
from sklearn.datasets import load_breast_cancer # this imports the dataset from sklearn library
from sklearn.metrics import confusion_matrix # to create the confusion matrix

# Importing model libraries
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from tensorflow import keras
import numpy as np

# Visualization
import matplotlib.pyplot as plt # Plotting library
import seaborn as sns # Visualization library
from PIL import Image # Pillow Image display
import requests # Request data from websites
from io import BytesIO # helps to fetch the sample image

# Run streamlit app
if __name__ == '__main__':
    st.title("$$Categorizing~Breast~Cancer$$") # the $$ are responsbile for the font, ~ equals a space
    st.title("$$With~Machine~Learning$$")
    st.write("This webapp will use a sequential neural network to predict the severity of breast cancer cases.")
    st.write("_By: So spontan jetzt_") # _ makes the font italic
    st.write("")
    st.write("")
    st.write("")
    st.write("")

# Preparing the data and first split into features and labels
breastcancer_dataset = load_breast_cancer()
X = breastcancer_dataset.data
y = breastcancer_dataset.target
sts = StandardScaler() # standardizes our data (increased model performance)
X_s = sts.fit_transform(X) 


# Visualizing the dataset
st.subheader("$$Data~Visualization$$")
# Scans 
st.write("")
st.write("Images show microscope pictures of fine needle aspirates (FNA) of cancerous breast mass.")
st.write("")

# Requesting a sample image from medium
sample_image_fetch = requests.get("https://miro.medium.com/v2/resize:fit:720/format:webp/1*pxFCmhRFTighUn88baLcSA.png")
sample_image = Image.open(BytesIO(sample_image_fetch.content)) # BytesIO provides a way to create a file-like object from binary data
st.image(sample_image)

# Numeric data
st.write("")
st.write("The 10-row excerpt of the 569-entry dataset below shows with our target and the correlating measurements represented by float numbers.")
st.write("")
bc_numeric = pd.DataFrame(  # function to create a pandas dataframe (nice for visualization and many data science tasks)
    data=breastcancer_dataset["data"], # inputs the feature data from our original dataset
    columns=breastcancer_dataset["feature_names"] # sets the feature names as table header
)
bc_numeric.insert(loc=0, column="target", value=breastcancer_dataset["target"]) # adds our target data to this table
bc_w_label = bc_numeric.copy()
bc_w_label['target'] = bc_numeric['target'].replace({0: "malignant", 1: "benign"}) # replace zeros and ones of the target data with malignant/benign
st.table(bc_w_label.iloc[50:60, :]) # shows the data sample table via streamlit
st.write("")
st.write("Correlations between data and targets")
st.write("")
crr = bc_numeric.corr() # setting up the correlations of our bc_numeric dataframe
correlations = crr["target"].sort_values(ascending=False) # setting up the correlation in descending order
st.table(correlations.head(30)) # shows the data sample table via streamlit
st.write("")
st.write("")
st.write("")
st.write("")


# Retrieving the input data from streamlits slider function
st.subheader("$$Model~Adaption~And~Performance$$")
test_data_input = st.slider("Select the percentage of the data to be earmarked as testing data:",0, 100, 30, 1) # defines the slider, for details hover over "slider"
test_data_percentage = test_data_input / 100 # shaping the input to a processable format (from 30 to 0.3)
# st.write("Ratio of test data = ", test_data_input, "%")
st.write("$$ Ratio~of~test~data = \\frac{test~data}{total~total} $$",f"$$= {test_data_input}\\% $$")
X_train, X_test, y_train, y_test = train_test_split(X_s, y, test_size=test_data_percentage) # randomly assigns (input)% of the data as "test data"

# Building and compiling the neural network
nn_clf = Sequential([
    #keras.layers.Flatten(input_shape=[A,A]) for pictures
    keras.layers.Dense(30,activation="relu"), # input layer for our 30 feature values
    keras.layers.Dense(300,activation="relu"), # hidden layer, 300 perceptrons
    keras.layers.Dense(100,activation="relu"),  # hidden layer, 300 perceptrons
    keras.layers.Dense(1,activation="sigmoid")  # output layer, 1 perceptron, represents a probability between [0,1)
])
nn_clf.compile(loss="binary_crossentropy",optimizer="adam",metrics="accuracy") # fixing loss function, optimizer and performance rating
nn_clf.fit(X_train,y_train,epochs=30,batch_size=32) # defining the training plan (30 iterations, 32 datapoints each time)
y_pred = nn_clf.predict(X_test)
y_pred_classes = (y_pred > 0.5).astype(int) # since the output is a probability, we must convert it into EITHER 0 or 1
loss, accuracy = nn_clf.evaluate(X_test, y_test)  # self evaluation

# Print the final accuracy
print("Final Accuracy:", accuracy)
accuracy_percentage = round(accuracy*100,1) # Equal to accuracy_score(y_test, y_pred)
# Streamlit Display of Results
st.write("$$ Accuracy = \\frac{correctly~classified~samples}{total~number~of~samples} $$",f"$$= {accuracy_percentage}\\% $$") # correctly classified samples divided by the total number of samples
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")

# Confusion matrix setup and display
st.subheader("$$Confusion~Matrix$$")
st.write("")
cmx = confusion_matrix(y_test, y_pred_classes) # calculating the confusion matrix
xylabels = ["Malignant","Benign"]
st.set_option("deprecation.showPyplotGlobalUse", False) # Suppresses an error display
sns.heatmap(cmx, # create heatmap from our confusion matrix
            annot=True, # To show the numbers in the fields
            fmt="d", # To avoid scientific notation like 2.4e-03 in the fields
            cmap="Blues", # Used color scheme
            xticklabels=xylabels,
            yticklabels=xylabels,
            )
plt.xlabel("Actual")
plt.ylabel("Predicted")
st.pyplot()
st.write("")
st.write("")
st.write("")
st.write("")

# Specificity and sensitivity analysis
st.subheader("$$Specificity~And~Sensitivity$$")
# Extracting the values for our sensitivity and specificity formulas from the confusion matrix
TP = cmx[0][0] # True Positives
TN = cmx[1][1] # True Negatives
FP = cmx[0][1] # False Positives
FN = cmx[1][0] # False Negatives
# calculating specificity and sensitivity of the test dataset
sensitivity = round((TP / (TP + FN))*100,1)
specificity = round((TN / (TN + FP))*100,1)
st.write("")
st.write("")
# explaining specificity and sensitivity with natural language and formulas
st.write("Sensitivity (also: True Positive (Malignant) Rate TPR):")
st.write("$$ TPR = \\frac{TP}{TP + FN} $$","$$= \\frac{True Malignant}{True Malignant + False Benign} $$",f"$$= \\frac{{{TP}}}{{{TP} + {FN}}} = {sensitivity}\\% $$")# LaTeX formatting for the sensitivity formula
st.write("")
st.write("")
st.write("Specificity (also: True Negative (Benign) Rate TNR):")
st.write("$$ TNR = \\frac{TN}{TN + FP} $$","$$= \\frac{True Benign}{True Benign + False Malignant} $$",f"$$= \\frac{{{TN}}}{{{TN} + {FP}}} = {specificity}\\% $$")# LaTeX formatting for the specificity formula
