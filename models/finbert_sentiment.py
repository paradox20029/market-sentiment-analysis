"""FinBERT sentiment wrapper with a safe fallback.

This module avoids importing heavy native libraries (torch) at import time
so that machines with broken or incompatible torch installations ( DLL
initialization failures like WinError 1114 ) can still import the package.
If the transformers/torch stack is available the class will load the
pretrained FinBERT model. If not, a lightweight keyword-based heuristic
is used as a fallback.
"""

try:
    # Try dynamic import of heavy dependencies. If this fails (for example
    # because torch cannot initialize a native DLL on Windows), we keep a
    # flag and fall back to a simple heuristic later.
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    _TRANSFORMERS_AVAILABLE = True
    _IMPORT_ERROR = None
except Exception as _e:
    _TRANSFORMERS_AVAILABLE = False
    _IMPORT_ERROR = _e


class FinBERT:
    def __init__(self):
        self.model_name = "yiyanghkust/finbert-tone"
        self.available = False
        self._init_error = None

        if _TRANSFORMERS_AVAILABLE:
            try:
                # Lazy but explicit model/tokenizer load. This may download
                # the model on first run and requires internet + disk space.
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name
                )
                self.available = True
            except Exception as e:
                # If model download or initialization fails, record the
                # error and fall back to the heuristic below.
                self._init_error = e
                self.available = False
        else:
            # Record why the real model isn't available.
            self._init_error = _IMPORT_ERROR

    def predict(self, text: str) -> str:
        """Return one of: 'Negative', 'Neutral', 'Positive'.

        If the FinBERT model is available it will be used. Otherwise a
        lightweight keyword-rule heuristic is applied so the rest of the
        pipeline can run without heavy dependencies.
        """
        # Try model-based prediction when available
        if self.available:
            try:
                tokens = self.tokenizer(
                    text, return_tensors="pt", truncation=True, padding=True
                )
                outputs = self.model(**tokens)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                sentiment_idx = int(torch.argmax(probs).item())
                labels = ["Negative", "Neutral", "Positive"]
                return labels[sentiment_idx]
            except Exception:
                # On any runtime failure fall back to heuristic below.
                pass

        # Heuristic fallback: simple keyword scoring (no external deps).
        txt = (text or "").lower()
        # Small positive/negative lexicons tuned for financial headlines.
        pos_words = [
            "good",
            "great",
            "positive",
            "gain",
            "up",
            "rise",
            "bull",
            "beat",
            "beats",
            "surge",
            "record",
            "strong",
            "growth",
            "increase",
            "outperform",
        ]
        neg_words = [
            "bad",
            "poor",
            "negative",
            "loss",
            "down",
            "drop",
            "fall",
            "bear",
            "miss",
            "missed",
            "decline",
            "weak",
            "decrease",
            "cut",
        ]

        score = 0
        for w in pos_words:
            if w in txt:
                score += 1
        for w in neg_words:
            if w in txt:
                score -= 1

        if score > 0:
            return "Positive"
        elif score < 0:
            return "Negative"
        else:
            return "Neutral"

    def is_available(self) -> bool:
        """Return True when the real FinBERT model is loaded and usable."""
        return self.available

