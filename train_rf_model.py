from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

import numpy as np
import pandas as pd
import io
import seaborn as sns
import matplotlib.pyplot as plt
import joblib


# Load CSV file
df = pd.read_csv('paino_fingering.csv')

# Enriching with more features
df['prev_pitch'] = df.groupby(['title', 'hand'])['pitch'].shift(1, fill_value = -1)
df['prev_pitch'] = df['prev_pitch'] - df['pitch']
df['prev_finger'] = df.groupby(['title', 'hand'])['finger'].shift(1, fill_value = -1)

df['prev_prev_pitch'] = df.groupby(['title', 'hand'])['pitch'].shift(2, fill_value = -1)
df['prev_prev_pitch'] = df['prev_prev_pitch'] - df['pitch']
df['prev_prev_finger'] = df.groupby(['title', 'hand'])['finger'].shift(2, fill_value = -1)

# Features
data = df[["hand", "pitch",	"finger", "is_chord", "prev_pitch", "prev_finger", "prev_prev_pitch", "prev_prev_finger"]]

# Only fingered samples
data = data[data['finger'] > 0]

# Shuffle
data = data.sample(frac=1)


# Separate features (X) and target (y)
X = data.drop('finger', axis=1).values
y = data['finger'].values  # Replace 'finger' with the name of your target column

# Split the data into training and testing sets (90% training and 10% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

# Initialize and train the RandomForestClassifier
rf = RandomForestClassifier(random_state=42)
rf.fit(X_train, y_train)

# Predict on the test set and evaluate 
train_accuracy = accuracy_score(y_train, rf.predict(X_train))
test_accuracy = accuracy_score(y_test, rf.predict(X_test))

# Accuracy
print("Training Set Accuracy:", train_accuracy)
print("Test Set Accuracy:", test_accuracy)

# Feature importance
importances = rf.feature_importances_
print(importances)
plt.bar(["Hand", "Pitch\n(MIDI)",	"Is\nChord", "Prev\nPitch", "Prev\nFinger", "Prev\nPrev\nPitch", "Prev\nPrev\nFinger"], importances)
plt.savefig('img/importances.png')

# Create the confusion matrix
cm = confusion_matrix(y_test, rf.predict(X_test))
finger_labels = ['1', '2', '3', '4', '5']

# Plot the confusion matrix as a heatmap
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=finger_labels, yticklabels=finger_labels)
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.savefig('img/cm.png')

# Export
# Save the model to a file
joblib.dump(rf, 'rf_model.joblib')
