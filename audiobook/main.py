import os
import pyttsx3
import PyPDF2
import logging

logger = logging.getLogger("PyPDF2")
logger.setLevel(logging.INFO)

speed_dict = {
    "slow": 100,
    "normal": 150,
    "fast": 200}


def speak_text(engine, text, display=True):
    if display:
        print(text)
    engine.say(text)
    engine.runAndWait()


class AudioBook:
    """
    AudioBook class
    
    methods:
        file_check: checks if file exists
        pdf_to_json: converts pdf to json format
        create_json_book: Creates json book from input file by calling respective method
        save_audio: saves audio files in folder
        read_book: reads the book
        
    sample usage:
        ab = AudioBook(speed="normal")
        ab.read_book(file_path, password="abcd")
    """
    
    def __init__(self, speed="normal"):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", speed_dict[speed])
    
    def file_check(self, file_path):
        """ 
        checks file format and if file exists
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found!")
      
    def pdf_to_json(self, input_file_path, password=None):
        """ 
            Converts pdf to json format
        """
        book_dict = {}
        with open(input_file_path, "rb") as fp:
            pdfReader = PyPDF2.PdfFileReader(fp)
            if pdfReader.isEncrypted:
                logging.info("File is encrypted, trying to decrypt...")
                pdfReader.decrypt(password)
            pages = pdfReader.numPages
            for num in range(0, pages):
                pageObj = pdfReader.getPage(num)
                text = pageObj.extractText()
                book_dict[num] = text
        return book_dict, pages
    
    def txt_to_json(self, input_file_path):
        book_dict = {}
        with open(input_file_path, "r") as fp:
            file_data = fp.read()
        
        # split text into pages of 2000 characters
        for i in range(0, len(file_data), 2000):
            book_dict[i] = file_data[i:i+2000]
        return book_dict, len(book_dict)
        
    def create_json_book(self, input_file_path, password=None):
        self.file_check(input_file_path)
        if input_file_path.endswith(".pdf"):
            book_dict, pages = self.pdf_to_json(input_file_path, password)
        elif input_file_path.endswith(".txt"):
            book_dict, pages = self.txt_to_json(input_file_path)
        return book_dict, pages
    
    def save_audio(self, input_file_path, password=None):
        self.file_check(input_file_path)
        with open(input_file_path, "rb") as fp:
            basename = os.path.basename(input_file_path).split(".")[0]
            os.makedirs(basename, exist_ok=True)
            logging.info('Saving audio files in folder: {}'.format(basename))
            pdfReader = PyPDF2.PdfFileReader(fp)
            if pdfReader.isEncrypted:
                logging.info("File is encrypted, trying to decrypt...")
                pdfReader.decrypt(password)
            pages = pdfReader.numPages
            for num in range(0, pages):
                pageObj = pdfReader.getPage(num)
                text = pageObj.extractText()
                self.engine.save_to_file(text, os.path.join(basename, basename + "_" + (str(num) + ".mp3")))
                self.engine.runAndWait()
                
    def read_book(self, input_file_path, password=None):
        self.file_check(input_file_path)
        print("Creating your audiobook... Please wait...")
        book_dict, pages = self.create_json_book(input_file_path, password)
        speak_text(self.engine, f"The book has total {str(pages)} pages!")
        speak_text(self.engine, "Please enter the page number: ", display=False)
        start_page = int(input("Please enter the page number: ")) - 1
                        
        reading = True
        while reading:
            if start_page > pages or start_page < 0:
                speak_text(self.engine, "Invalid page number!")
                speak_text(self.engine, f"The book has total {str(pages)} pages!")
                start_page = int(input("Please enter the page number: "))

            speak_text(self.engine, f"Reading page {str(start_page+1)}")
            pageText = book_dict[start_page]
            speak_text(self.engine, pageText, display=False)

            user_input = input("Please Select an option: \n 1. Type 'r' to read again: \n 2. Type 'p' to read previous page\n 3. Type 'n' to read next page\n 4. Type 'q' to quit:\n 5. Type page number to read that page:\n")
            if user_input == "r":
                speak_text(self.engine, f"Reading page {str(start_page+1)}")
                continue
            elif user_input == "p":
                speak_text(self.engine, "Reading previous page")
                start_page -= 1
                continue
            elif user_input == "n":
                speak_text(self.engine, "Reading next page")
                start_page += 1
                continue
            elif user_input == "q":
                speak_text(self.engine, "Quitting the book!")
                break
            elif user_input.isnumeric():
                start_page = int(user_input) - 1
            else:
                user_input = input("Please Select an option: \n 1. Type 'r' to read again: \n 2. Type 'p' to read previous page\n 3. Type 'n' to read next page\n 4. Type 'q' to quit:\n 5. Type page number to read that page:\n")
                continue
