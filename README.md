# Piano Fingering Prediction Project

![Enter image alt description](img/notes_with_fingering.png)

## Abstract

This project leverages machine learning to predict piano fingering for musical scores. It uses real-world annotated piano scores, processes them to extract meaningful features, trains a Random Forest model, and applies the model to annotate unseen scores with predicted fingering.




## Problem Overview

Determining optimal piano fingering for a given score is a challenging task, influenced by musical, physiological, and stylistic factors. Current solutions rely on manual annotation, which can be time-consuming and inconsistent. This project automates fingering prediction using machine learning techniques, making it a valuable tool for learners, educators, and composers.




## Project Overview

The project consists of three main components:

**Training Data Preparation**:

1. Parsed publicly available MusicXML files with fingering annotations using the music21 library.

2. Extracted features such as note pitch, chord information, and sequential context (e.g., previous notes and fingers).

3. Combined extracted data into a structured CSV dataset (piano_fingering.csv) for training.

**Model Training and Evaluation**:

1. Engineered features for the Random Forest model, including relative pitch differences and previous fingering data.

2. Trained a Random Forest Classifier and evaluated its performance using accuracy and confusion matrices.

3. Saved the trained model for future use.

**Application**:

1. Created a script to apply the trained model to new scores, annotating them with predicted fingering.

2. Integrated the functionality into a Python pipeline for automated processing of unseen scores.



## Dependencies and Setup

The following tools and libraries were used in the project:

1. **MuseScore**: A free, open-source music notation program that includes features for creating and editing scores.

2. **music21**: An object-oriented toolkit for analyzing, searching, and transforming music in symbolic (score- based) forms.

3. **MuseScore.com:** A website that allows users to share, save, and publish sheet music online.

4. **MusicXML:** is a format for sharing digital sheet music between applications. It's an open, flexible, and human-readable format that uses XML to represent musical elements. 



### Installation

```shell
# Install MuseScore
sudo add-apt-repository ppa:mscore-ubuntu/mscore3-stable -y
sudo apt-get update
sudo apt-get install musescore3

# Install libraries
pip install music21
pip install musicxml

# Configure Music21
python3 -c "from music21 import configure; configure.run()"
```




## **Data Preparation**

- Collected piano scores (in MusicXML format) from Musescore.com, focusing on publicly available scores with fingering annotations.

- Processed 32 scores, containing over 31,000 notes, of which 13,000 had fingering annotations.

- Extracted data for each hand (right/left), including notes, chords, rests, and their associated fingerings.

- Stored the processed dataset in `piano_fingering.csv`.

![Enter image alt description](img/finger_dist.png)

![Enter image alt description](img/pitch_dist.png)

**Details**: See `example_gen.py`.



## **Training**

**Feature Engineering**: Added sequential features for the previous two notes and their respective fingerings, as well as relative pitch differences.

**Model Training**: Trained a Random Forest model on 90% of the dataset, reserving 10% for testing.

**Features Used**:

- Hand (left/right)

- Pitch (MIDI number)

- Is part of a chord

- Previous note's pitch and finger

- Previous-previous note's pitch and finger

**Results**:

- Training Accuracy: 95.05%

- Testing Accuracy: 77.71%

**Details**: See `train_rf_model.py`.




## **Evaluation**

- Training Accuracy: 95.05%

- Testing Accuracy: 77.71%

### **Feature Importance**

The importance of features in the Random Forest model

![Enter image alt description](img/importances.png)

### **Confusion Matrix**

![Enter image alt description](img/cm.png)



## **Fingering Application**

The trained model was applied to new scores to predict fingering. The `fingering_application.py` script iterates over MusicXML files, predicts fingering for each note based on context, and outputs the annotated score.

Example: Twinkle, Twinkle, Little Star (model generated fingering):

![Enter image alt description](img/twinkle_with_fingering.png)



## **Future Work**

1. Experiment with alternative models (e.g., Gradient Boosting, SVM, XGBoost).

2. Generate synthetic training data using music theory heuristics.

3. Add forward-looking features, note duration, and rhythmic patterns for improved prediction.



## **Conclusion**

This project demonstrates how machine learning can automate piano fingering prediction. While initial results are promising, further refinement in data and models can make this tool invaluable for music education and composition.



## **Files**

- `example_gen.py`: Script for data preparation.

- `train_rf_model.py`: Script for training and evaluating the Random Forest model.

- `fingering_application.py`: Script for updating fingering in a score using trained Random Forest model.

- `piano_fingering.csv`: Prepared dataset.

- `rf_model.joblib`: Trained Random Forest model for inference.
