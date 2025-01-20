from music21 import *
import pandas as pd
from os import listdir
from os.path import isfile, join

us = environment.UserSettings()
us["musescoreDirectPNGPath"] = "/usr/bin/mscore3"
us["directoryScratch"] = "/tmp"


def extract_fingering_to_dataframe(score_path):
    """
    Extracts fingering information from a MusicXML file and stores it in a Pandas DataFrame.
    
    Args:
        score_path (str): Path to MusicXML score.
    
    Returns:
        pd.DataFrame: A DataFrame containing note details and fingering information.
    """
    
    # Parse score
    score = converter.parse(score_path)
    
    
    # Initialize a list to store the data
    data = []
    
    # Iterate over the notes and chords
    # Assume part 0 = Right Hand, part 1 = Left Hand
    for part_index, part in enumerate(score.parts):
        
        for n in part.recurse():
            if isinstance(n, note.Note):  # Single note
                # Check for fingering articulations in the note
                fingers = [
                    art.fingerNumber for art in n.articulations
                    if isinstance(art, articulations.Fingering)
                ]
                data.append({
                    "title": score_path,
                    "note": n.nameWithOctave,
                    "pitch": n.pitch.midi, # MIDI number of the pitch
                    "fingering": fingers[0] if fingers else 0,
                    "is_chord": False,
                    "is_rest": False,
                    "hand": part_index
                })
            elif isinstance(n, chord.Chord):  # Chord
                fingers = [
                    art.fingerNumber for art in n.articulations
                    if isinstance(art, articulations.Fingering)
                ]
                for pitch, finger in zip(n.pitches, fingers):
                    data.append({
                        "title": score_path,
                        "note": pitch.nameWithOctave,
                        "pitch": pitch.midi,
                        "fingering": finger if finger else 0,
                        "is_chord": True,
                        "is_rest": False,
                        "hand": part_index
                    })
            elif isinstance(n, note.Rest):  # Rest
                data.append({
                    "title": score_path,
                    "note": "Rest",
                    "pitch": 0,
                    "fingering": 0,
                    "is_chord": False,
                    "is_rest": True,
                    "hand": part_index
                })
    
    # Convert the list of dictionaries into a Pandas DataFrame
    df = pd.DataFrame(data)
    return df




dataset = pd.DataFrame(columns=["title", "note", "pitch", "fingering", "is_chord", "is_rest", "hand"]);

files = [join("data/", f) for f in listdir("data/") if isfile(join("data/", f))]
dataset_chunks = []

for f in files:
    print(f)
    dataset_chunks.append(extract_fingering_to_dataframe(f))

dataset = pd.concat(dataset_chunks)
dataset.fillna(0, inplace=True)
dataset['finger'] = dataset['fingering'].astype(str).str.extract('(\d)').fillna(0).astype(int)

dataset.to_csv('paino_fingering.csv', index = False);
