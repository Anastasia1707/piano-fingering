import pandas as pd
from music21 import *

# Install libraries:
#   pip install musicxml
#   pip install music21
#
# Run this once (first time setup):
#   configure.run()


# Extracts first finger articulation.
def get_finger(n, j=0):
    fingers = []
    for art in n.articulations:
        if isinstance(art, articulations.Fingering):
            fingers.append(art.fingerNumber)
    finger = 0
    if len(fingers) > j:
        finger = fingers[j]
    return finger


# Extracts fingers articulation for chord or zeros.
def get_fingers_from_chord(chord):
    fingers = []
    # Extract array of articulations/fingers.
    for art in chord.articulations:
        if isinstance(art, articulations.Fingering):
            fingers.append(art.fingerNumber)
    # If no fingers specified, return zeros.
    if not fingers:
        for note in chord.notes:
            fingers.append(0)
    return fingers


# Populates Dataframe (df) with notes extracted from score
def parse_score(file, df):
    # Try to parse file using MusicXML converter.
    score = converter.parse(file)
    file = file.replace('data/input/', '').replace('.mxl', '')

    # Each score typically has two parts (one for each hand)
    for part in score.parts:
        # A  measure, also known as a bar, is a segment of music
        # that's separated from the next measure by a vertical line called a barline.
        for measure in part.getElementsByClass('Measure'):
            # print(measure)
            for element in measure.notesAndRests:
                # print(element)
                # Elements are either notes, chords or rest:
                if element.isNote:
                    df.loc[len(df)] = pd.Series(
                        {'title': file, 'part': part.id, 'measure': measure.number,
                         'note': element.pitch, 'name': element.name,
                         'octave': element.octave, 'finger': get_finger(element), 'is_chord': False, 'is_rest': False})
                elif element.isChord:
                    for note_and_finger in zip(element.notes, get_fingers_from_chord(element)):
                        note = note_and_finger[0]
                        finger = note_and_finger[1]
                        df.loc[len(df)] = pd.Series(
                            {'title': file, 'part': part.id, 'measure': measure.number,
                             'note': note.pitch, 'name': note.name,
                             'octave': note.octave, 'finger': finger, 'is_chord': True, 'is_rest': False})
                elif element.isRest:
                    df.loc[len(df)] = pd.Series(
                        {'title': file, 'part': part.id, 'measure': measure.number, 'is_chord': False,
                         'is_rest': True})
                else:
                    print("Unknown type")


# Parse score files (GZip/MusicXML)
# Add more files from directory
files = ['data/art_of_fugue.mxl', 'data/fantasia.mxl', 'data/fr_elise.mxl']
dataset = pd.DataFrame(columns=['title', 'part', 'measure', 'note', 'name', 'octave', 'finger', 'is_chord', 'is_rest']);

for file in files:
    print(file)

    parse_score(file, dataset)

# Lookup first 40 rows:
print(dataset.head(40))
# Lookup first 40 rows (second hand):
print(dataset.query('part == "P1-Staff2"').head(40))
print(dataset.query('title == "fantasia"').head(40))
print(dataset.count())
print(dataset[dataset.finger > 0].count())