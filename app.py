import streamlit as st
import pandas as pd
import numpy as np
import joblib
import tempfile
import os
from music21 import converter, note, chord, articulations, environment

# Suppress music21 warnings about missing MuseScore
environment.set("musescoreDirectPNGPath", "")
environment.set("musicxmlPath", "")

st.set_page_config(page_title="Piano Fingering Predictor", page_icon="🎹", layout="centered")

st.title("Piano Fingering Predictor")
st.markdown(
    "Upload a MusicXML (`.mxl` or `.musicxml`) file and get predicted fingerings "
    "added to your score using a Random Forest model trained on 43 annotated piano pieces."
)


@st.cache_resource
def load_model():
    return joblib.load("rf_model.joblib")


def extract_features(score):
    """Parse a music21 score and build the same feature set used during training."""
    rows = []
    note_map = []  # keeps a reference to each note/chord for writing back

    for part_index, part in enumerate(score.parts):
        part_rows = []
        part_notes = []

        for n in part.recurse():
            if isinstance(n, note.Note):
                part_rows.append({
                    "pitch": n.pitch.midi,
                    "is_chord": False,
                    "is_rest": False,
                    "hand": part_index,
                })
                part_notes.append(n)

            elif isinstance(n, chord.Chord):
                for p in n.pitches:
                    part_rows.append({
                        "pitch": p.midi,
                        "is_chord": True,
                        "is_rest": False,
                        "hand": part_index,
                    })
                    part_notes.append(n)

            elif isinstance(n, note.Rest):
                part_rows.append({
                    "pitch": 0,
                    "is_chord": False,
                    "is_rest": True,
                    "hand": part_index,
                })
                part_notes.append(n)

        rows.extend(part_rows)
        note_map.extend(part_notes)

    df = pd.DataFrame(rows)
    return df, note_map


def add_context_features(df):
    """Add previous/next pitch differences and finger columns (set to 0 for inference)."""
    df["finger"] = 0  # placeholder — model predicts this

    # Previous notes (pitch differences)
    for i, label in enumerate(["prev_pitch", "prev_prev_pitch", "prev_prev_prev_pitch", "prev_prev_prev_prev_pitch"], start=1):
        shifted = df.groupby("hand")["pitch"].shift(i).fillna(-1)
        df[label] = df["pitch"] - shifted

    # Previous fingers (unknown at inference — use 0)
    for label in ["prev_finger", "prev_prev_finger", "prev_prev_prev_finger", "prev_prev_prev_prev_finger"]:
        df[label] = 0

    # Next notes (pitch differences)
    for i, label in enumerate(["next_pitch", "next_next_pitch"], start=1):
        shifted = df.groupby("hand")["pitch"].shift(-i).fillna(-1)
        df[label] = shifted - df["pitch"]

    # Next fingers (unknown)
    for label in ["next_finger", "next_next_finger"]:
        df[label] = 0

    return df


def build_feature_matrix(df):
    """Select and order columns to match the training feature set."""
    feature_cols = [
        "hand", "pitch", "is_chord",
        "prev_pitch", "prev_finger", "prev_prev_pitch", "prev_prev_finger",
        "prev_prev_prev_pitch", "prev_prev_prev_finger",
        "prev_prev_prev_prev_pitch", "prev_prev_prev_prev_finger",
        "next_pitch", "next_finger", "next_next_pitch", "next_next_finger",
    ]
    return df[feature_cols].values


def write_fingerings_to_score(score, note_map, predictions):
    """Write predicted fingerings back into the music21 score objects."""
    seen = set()
    pred_idx = 0

    for part_index, part in enumerate(score.parts):
        for n in part.recurse():
            if isinstance(n, note.Note):
                finger = int(predictions[pred_idx])
                if finger > 0:
                    n.articulations = [
                        a for a in n.articulations
                        if not isinstance(a, articulations.Fingering)
                    ]
                    n.articulations.append(articulations.Fingering(finger))
                pred_idx += 1

            elif isinstance(n, chord.Chord):
                for p in n.pitches:
                    finger = int(predictions[pred_idx])
                    if finger > 0:
                        # Add fingering for chord notes
                        n.articulations = [
                            a for a in n.articulations
                            if not isinstance(a, articulations.Fingering)
                        ]
                        n.articulations.append(articulations.Fingering(finger))
                    pred_idx += 1

            elif isinstance(n, note.Rest):
                pred_idx += 1

    return score


# --- UI ---

model = load_model()

uploaded = st.file_uploader("Upload a MusicXML file", type=["mxl", "musicxml", "xml"])

if uploaded is not None:
    with st.spinner("Parsing score..."):
        # Save upload to a temp file so music21 can read it
        suffix = os.path.splitext(uploaded.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        score = converter.parse(tmp_path)

    st.success(f"Parsed **{uploaded.name}** — {len(score.parts)} part(s) found.")

    with st.spinner("Predicting fingerings..."):
        df, note_map = extract_features(score)
        df = add_context_features(df)
        X = build_feature_matrix(df)
        predictions = model.predict(X)
        score = write_fingerings_to_score(score, note_map, predictions)

    st.success("Fingerings predicted!")

    # Show a quick summary
    unique, counts = np.unique(predictions[predictions > 0], return_counts=True)
    summary = pd.DataFrame({"Finger": unique.astype(int), "Count": counts})
    st.bar_chart(summary.set_index("Finger"))

    # Export
    with st.spinner("Exporting annotated score..."):
        out_path = tempfile.mktemp(suffix=".musicxml")
        score.write("musicxml", fp=out_path)
        with open(out_path, "rb") as f:
            out_bytes = f.read()

    base_name = os.path.splitext(uploaded.name)[0]
    st.download_button(
        label="Download annotated MusicXML",
        data=out_bytes,
        file_name=f"{base_name}_fingered.musicxml",
        mime="application/vnd.recordare.musicxml+xml",
    )

    # Cleanup temp files
    os.unlink(tmp_path)
    os.unlink(out_path)
