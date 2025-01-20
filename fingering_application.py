import joblib
import numpy as np

from music21 import *
from sklearn.ensemble import RandomForestClassifier



def predict_fingering(rf_model, hand, pitch, is_chord, prev_pitch, prev_finger, prev_prev_pitch, prev_prev_finger):
    """
    Predicts the fingering using the provided Random Forest model.
    
    Args:
        rf_model: The trained Random Forest model.
        hand (int): 0 for left hand, 1 for right hand.
        pitch (int): MIDI pitch of the current note.
        is_chord (bool): True if the note is part of a chord, False otherwise.
        prev_pitch (int): MIDI pitch of the previous note.
        prev_finger (int): Fingering of the previous note.
        prev_prev_pitch (int): MIDI pitch of the note before the previous one.
        prev_prev_finger (int): Fingering of the note before the previous one.
    
    Returns:
        int: Predicted fingering (1-5).
    """
    # Prepare the input feature array
    input_features = np.array([[hand, pitch, int(is_chord), prev_pitch - pitch, prev_finger, prev_prev_pitch - pitch, prev_prev_finger]])
    
    # Make the prediction using the model
    return rf_model.predict(input_features)[0]


def populate_score_with_fingering(score_path):
    """
    Extracts fingering information from a MusicXML file and stores it in a Pandas DataFrame.
    
    Args:
        score_path (str): Path to MusicXML score.
    
    Returns:
        pd.DataFrame: A DataFrame containing note details and fingering information.
    """
    
    # Parse score
    score = converter.parse(score_path)

    hand = 0
    pitch = 0  
    is_chord = False
    prev_pitch = 0 
    prev_finger = 0
    prev_prev_pitch = 0 
    prev_prev_finger = 0

    # Iterate over the notes and chords
    # Assume part 0 = Right Hand, part 1 = Left Hand
    for part_index, part in enumerate(score.parts):
        hand = part_index
        for n in part.recurse():
            if isinstance(n, note.Note):  # Single note
                pitch = n.pitch.midi
                is_chord = False
                finger = predict_fingering(rf, hand, pitch, is_chord, prev_pitch, prev_finger, prev_prev_pitch, prev_prev_finger)
                n.articulations.append(articulations.Fingering(finger))
                
                prev_prev_finger = prev_finger
                prev_prev_pitch = prev_pitch
                prev_pitch = pitch
                prev_finger = finger
            elif isinstance(n, chord.Chord):  # Chord
                for pitch in n.pitches:
                    is_chord = True
                    finger = predict_fingering(rf, hand, pitch.midi, is_chord, prev_pitch, prev_finger, prev_prev_pitch, prev_prev_finger)
                    n.articulations.append(articulations.Fingering(finger))
                    prev_prev_finger = prev_finger
                    prev_prev_pitch = prev_pitch
                    prev_pitch = pitch.midi
                    prev_finger = finger
    return score




# Load the model from the file
rf = joblib.load("rf_model.joblib")


# Call the function
print(f"Predicted finger: {predict_fingering(rf, 0, 64, False,	66,	3,	62,	1)}")
print(f"Predicted finger: {predict_fingering(rf, 1,	36,	False,	48,	1,	50,	1)}")

# Without fingering
score = converter.parse("sample/twinkle.mxl")
score.show()

# Update fingering
score_with_fingering = populate_score_with_fingering("sample/twinkle.mxl")
score_with_fingering.show()
