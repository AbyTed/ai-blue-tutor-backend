class Transcript():
    def __init__(self, text) -> None:
        self.text = text
    def __repr__(self) -> str:
        return f"Transcription: {self.text}"