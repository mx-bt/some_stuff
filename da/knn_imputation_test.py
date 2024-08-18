import pandas as pd

# Example train and test dataframes
train_data = pd.DataFrame({
    'Monat': [4, 5, 6, 7, 8, 9, 10, 11, 12],
    'Anzahl ausgeliehener Fahrräder': [250, 300, 350, 400, 450, 500, 550, 600, 650]
})

test_data = pd.DataFrame({
    'Monat': [1, 2, 3, 4, 5, 6],
    'Anzahl ausgeliehener Fahrräder': [110, 160, 210, 260, 310, 360]
})

dummy_monate_vorlage = [
    f"Monat_{i+1}" for i in range(12)
]

dummy_jahreszeit_vorlage = [
    f"Jahreszeit_{i+1}" for i in range(4)
]
# Create dummy variables for train and test data
train_data_dummies = pd.get_dummies(train_data, columns=['Monat'])
train_data_dummies = train_data_dummies.reindex(columns=list(set(train_data_dummies.columns.to_list()+dummy_monate_vorlage)), fill_value=0.0).astype(float)

test_data_dummies = pd.get_dummies(test_data, columns=['Monat'])
test_data_dummies = test_data_dummies.reindex(columns=list(set(test_data_dummies.columns.to_list()+dummy_monate_vorlage)), fill_value=0.0).astype(float)
# Ensure test data has the same dummy columns as train data


print(train_data_dummies.columns.to_list())

# Display the transformed dataframes
print("Train Data:")
display(train_data_dummies)
print("\nTest Data:")
display(test_data_dummies)
