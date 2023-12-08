# Import necessary libraries
from PIL import Image
import streamlit as st
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay, cohen_kappa_score

# Set the title of the Streamlit app
st.title('Multilayer Perceptron for Optical Recognition of Handwritten Digits')

# Load the Digits dataset from scikit-learn
digits = datasets.load_digits()

# Define the number of rows, columns, and total number of images to display
num_row = 2
num_col = 5
num = 10

# Get the subset of images and labels for display
images = digits.images[:num]
labels = digits.target[:num]

# Plot and display the images using Matplotlib
fig, axes = plt.subplots(num_row, num_col, figsize=(1.5*num_col, 2*num_row))
for i in range(num):
    ax = axes[i//num_col, i%num_col]
    ax.imshow(images[i], cmap='gray')
    ax.set_title('Label: {}'.format(labels[i]))
plt.tight_layout()
plt.savefig('digits.jpg')
plt.show()

# Open and display the sample image using PIL
sample_image = Image.open('digits.jpg')
st.image(sample_image, caption='Sample Handwritten Digits')

# Create a slider to adjust the train-test ratio of the digits dataset
ratio = st.slider('Adjust the train-test-ratio of the digits dataset:', min_value=0.1, max_value=0.9)

# Preprocess the dataset by reshaping the images and splitting into train and test sets
n_samples = len(digits.images)
data = digits.images.reshape((n_samples, -1))
X_train, X_test, y_train, y_test = train_test_split(data, digits.target, test_size=ratio, shuffle=False)

# Create and train the MLP classifier model
clf = MLPClassifier(random_state=1, max_iter=300).fit(X_train, y_train)

# Make predictions on train and test data
predTrain = clf.predict(X_train)
predTest = clf.predict(X_test)

# Calculate and display the training and testing accuracies
st.write("Training Accuracy:", accuracy_score(y_train, predTrain)*100, "%")
st.write("Testing Accuracy:", accuracy_score(y_test, predTest)*100, "%\n")

# Calculate the confusion matrix and display it using a ConfusionMatrixDisplay
cm = confusion_matrix(y_test, predTest, labels=clf.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=clf.classes_)
disp.plot()
plt.savefig('confusion_matrix.jpg')
plt.show()

# Calculate the Kappa statistic and display it
cohen_score = cohen_kappa_score(y_test, predTest)
st.write('Kappa statistic:', cohen_score)

# Open and display the confusion matrix image using PIL
confusion_matrix_image = Image.open('confusion_matrix.jpg')
st.image(confusion_matrix_image, caption='Confusion Matrix on Test Data')

# Run the Streamlit app and generate the logs
# streamlit run /content/app.py &>/content/logs.txt &

# Display the URL to run the app using localtunnel
#!npx localtunnel --port 8501
 

