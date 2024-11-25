# Japanese Dictionary Microservice

## Communication Contract
### 1 - Endpoint: `/process`
- **Method**: POST
- **Request Parameters**:
  - `file`: The file to be processed (TXT or PDF).
  - `category`: The category of words (nouns, verbs, adjectives, adverbs, particles, or katakana).
  - `level`: The proficiency level (N1, N2, N3, N4, N5).

### Endpoint: `/download`
- **Method**: GET
- **Request Parameters**:
  - filename: categorylevel(timestamp).txt(.pdf) or invalid_words_categorylevel(timestamp).txt(.pdf)
  - host: localhost:5012/download/filename  


### 2 - Example Call 
(from terminal)
curl -X POST http://localhost:5012/process \
  -F "file=@test_words.txt" \ 
  -F "category=nouns" \       
  -F "level=N5"              

 Uploading Files:
 - file_name.txt(.pdf)
 - line format: kanji: hiragana = definition
 - if not in the above format, the miceo service will process the correct words but create a file with the invalid words

 Categories:
 - Nouns
 - Verbs
 - Adjectives
 - Adverbs
 - Particles 
 - Katakana

 Levels:
 - N5
 - N4
 - N3
 - N2
 - N1


### 3 - Example: Retrieving Data Request
succesfully parsed file ->  curl -O http://localhost:5012/download/N5_nouns_20241117-221200.txt

invalid words file -> curl -O http://localhost:5012/download/invalid_words_N5_nouns_20241117-221200.txt


### 3 - Example Response 

Full Sucessful Response
{
  "message": "Success: File processed successfully as {catagory} - {level}.",
  "processed_file": "N5_nouns_20241117-220956.txt",
  "processed_file_url": "http://localhost:5012/download/N5_nouns_20241117-220956.txt",
  "invalid_file": null,
  "invalid_file_url": null
}


Partial Success Response
{
  "message": "Partial Success: The file 'n4adj-copy-invalid.txt' was processed as nouns and N5, however, some line errors occurred.",
  "processed_file": "N5_nouns_20241117-221200.txt",
  "processed_file_url": "http://localhost:5012/download/N5_nouns_20241117-221200.txt",
  "invalid_file": "invalid_words_N5_nouns_20241117-221200.txt",
  "invalid_file_url": "http://localhost:5012/download/invalid_words_N5_nouns_20241117-221200.txt"
}


File Type Error Response
{
    "error": "Invalid file type. Only TXT and PDF are allowed."
}

No File Provided Response
{
    "error": "No file provided."
}


### -4. Mitigation Plan

#### **For which teammate did you implement “Microservice A”?**
- Anna Ryplewski

#### **What is the current status of the microservice?**
- Complete: The microservice is complete and ready for use.

#### **How is your teammate going to access your microservice?**
- Instructions for accessing the microservice:
  - Code Provide through shared discord server
  - requirements.txt file to install dependencies
  - Run the microservice locally (`python app.py`)
  - Send Data to the microservice at `http://localhost:5012/process'
    - File name, level and category are required
  - Recieve a message with the results (JSON)
    - Sucess: No errors in uploaded files formatting 
    - Partial Sucess: Some words processed - Link given to view invalid words
  - Get the processed file and invalid words file from the micro service.

#### **What should your teammate do if they cannot access the microservice?**
- Contact me via our discord server.
- I am CST and generally available 9am - 2pm and in the evenings.

#### **Deadline for Reporting Issues**
- If you encounter issues, please notify via discord and I will respond within 2 - 4 hours."

#### **Additional Notes**
- Python 3.8+ 
- The microservice is designed to process TXT and PDF files only.
- The microservice pattern looks for Katakana: Hiragana = defintion.
    - The main pattern being : and =
- The process file removes special characters and spaces from the file.


### -5. UML Diagram 
- /uml/uml.png

 - Client (C) → Microservice (M):
     -POST /process with file, category, and level.

 - Microservice (M) → Processor (P):
    - Validate file and form data.

 - Processor (P) → Microservice (M):
    - Return processed data and invalid lines.

 - Microservice (M) → FileSystem (F):
    - Save processed file.

 - If Partial Success:
    - Microservice (M) → FileSystem (F): Save invalid lines file.
    - Microservice (M) → Client (C): JSON Response (message, processed_file, invalid_file).

 - If Full Success:
    - Microservice (M) → Client (C): JSON Response (message, processed_file, invalid_file=null).

 - Client (C) → Microservice (M):
    - GET /download/<processed_file>.
    - GET /download/<invalid_file>.

 - Microservice (M) → FileSystem (F):
    - Retrieve invalid lines file.
    - Retrieve processed file.

 - Microservice (M) → Client (C):
    - Return invalid lines file.
    - Return processed file.
