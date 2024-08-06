class Form:
    def __init__(self, request, os):
        self.request = request
        self.os = os
        self.saved_files = dict()
    def save_files(self):
        files = {
            'audio': False 
        }
        print(self.request.files)
        if 'audio' in self.request.files:
            audio = self.request.files['audio']
            audio_path = self.os.path.join("UPLOAD AUDIO", audio.filename)
            audio.save(audio_path)
            files['audio'] = audio_path
            self.saved_files = files
        else:
            files = False
        return files

    def get_text(self):
        return self.request.form.get('text', '')

    def get_student_question(self):
        return self.request.form.get('studentQuestion', '')
    
    def cleanup_files(self):
        for file_path in self.saved_files.values():
            if self.os.path.exists(file_path):
                self.os.remove(file_path)