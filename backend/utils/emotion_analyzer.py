"""
Emotion Analyzer
----------------
Analyzes the emotional and tonal qualities of text using a pretrained RoBERTa model.
Returns emotion probabilities and dominant tones.
"""

from transformers import pipeline
import numpy as np

class EmotionAnalyzer:
    def __init__(self):
        self.analyzer = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)

    def analyze_tone(self, text: str):
        if not text.strip():
            return {"positivity": 0.5, "top_emotions": []}
        res = self.analyzer(text[:512])[0]
        emotions = {r["label"]: r["score"] for r in res}
        top = sorted(emotions, key=emotions.get, reverse=True)[:2]
        positivity = np.mean([emotions.get("joy", 0), emotions.get("optimism", 0)])
        return {"positivity": positivity, "top_emotions": top}
