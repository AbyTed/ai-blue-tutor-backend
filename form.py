class Form:
    def __init__(self, request, os, tempfile):
        self.request = request
        self.os = os
        self.saved_files = dict()
        self.tempfile = tempfile

    def save_files(self):
        files = {"audio": False}

        # Create a temporary directory
        temp_dir = self.tempfile.mkdtemp()

        # Get the audio file from the request
        audio_file = self.request.files.get("audio")

        if audio_file:
            # Save the file to the temporary directory
            audio_path = self.os.path.join(temp_dir, audio_file.filename)
            audio_file.save(audio_path)

            files["audio"] = audio_path
            self.saved_files = files
        else:
            files = False

        return files

    def get_text(self):
        return self.request.form.get("text", "")

    def get_student_question(self):
        return self.request.form.get("studentQuestion", "")

    def cleanup_files(self):
        for file_path in self.saved_files.values():
            if self.os.path.exists(file_path):
                self.os.remove(file_path)

    def __repr__(self) -> str:
        return f"saved_files: {self.save_files} "
