# Import necessary libraries
import os
import time
import re
import fitz
import openai
import numpy as np
import tensorflow_hub as hub
from sklearn.neighbors import NearestNeighbors

def process_pdf_files(input_folder, output_folder, question, instructions, openai_key, progress_callback=None):
    # Load the recommender model
    recommender = SemanticSearch()

    # Get the list of all files in the input folder
    all_files = os.listdir(input_folder)

    # Initialize the processing_times list
    processing_times = []

    # Iterate through each file in the input folder
    for index, filename in enumerate(all_files):
        print(f"Processing: {filename}")
        file_path = os.path.join(input_folder, filename)
        
        try:
            # Measure processing time for the current file
            start_time = time.time()

            # Load the recommender with the current file
            load_recommender(recommender, file_path) # Assuming this function is defined correctly

            # Generate the answer for the given question
            answer = generate_answer(recommender, question, instructions, openai_key)
            print(f"Answer generated: {answer}")

            # Save the answer to a text file in the output folder
            output_filename = os.path.splitext(filename)[0] + "_answer.txt"
            output_filepath = os.path.join(output_folder, output_filename)

            # Remove bracketed numbers from the answer
            cleaned_answer = remove_bracketed_numbers(answer)

            with open(output_filepath, "w") as output_file:
                output_file.write(cleaned_answer)
                print(f"Answer saved to: {output_filepath}")

            # Store the processing time for the current file
            end_time = time.time()
            processing_times.append(end_time - start_time)

        except Exception as e:
            print(f"Error processing {filename}: {e}")

        # Call the progress_callback function with the progress info
        if progress_callback is not None:
            progress_callback(index + 1, len(all_files))

    # Return the processing_times list
    return processing_times

def preprocess(text):
    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    return text

def pdf_to_text(path, start_page=1, end_page=None):
    doc = fitz.open(path)
    total_pages = doc.page_count

    if end_page is None:
        end_page = total_pages

    text_list = []

    for i in range(start_page-1, end_page):
        text = doc.load_page(i).get_text("text")
        text = preprocess(text)
        text_list.append(text)

    doc.close()
    return text_list

def text_to_chunks(texts, word_length=150, start_page=1):
    text_toks = [t.split(' ') for t in texts]
    page_nums = []
    chunks = []
    
    for idx, words in enumerate(text_toks):
        for i in range(0, len(words), word_length):
            chunk = words[i:i+word_length]
            if (i+word_length) > len(words) and (len(chunk) < word_length) and (
                len(text_toks) != (idx+1)):
                text_toks[idx+1] = chunk + text_toks[idx+1]
                continue
            chunk = ' '.join(chunk).strip()
            chunk = f'[{idx+start_page}]' + ' ' + '"' + chunk + '"'
            chunks.append(chunk)
    return chunks

class SemanticSearch:
    
    def __init__(self):
        self.use = hub.load('https://tfhub.dev/google/universal-sentence-encoder/4')
        self.fitted = False
    
    
    def fit(self, data, batch=1000, n_neighbors=5):
        self.data = data
        self.embeddings = self.get_text_embedding(data, batch=batch)
        n_neighbors = min(n_neighbors, len(self.embeddings))
        self.nn = NearestNeighbors(n_neighbors=n_neighbors)
        self.nn.fit(self.embeddings)
        self.fitted = True
    
    
    def __call__(self, text, return_data=True):
        inp_emb = self.use([text])
        neighbors = self.nn.kneighbors(inp_emb, return_distance=False)[0]
        
        if return_data:
            return [self.data[i] for i in neighbors]
        else:
            return neighbors
    
    
    def get_text_embedding(self, texts, batch=1000):
        embeddings = []
        for i in range(0, len(texts), batch):
            text_batch = texts[i:(i+batch)]
            emb_batch = self.use(text_batch)
            embeddings.append(emb_batch)
        embeddings = np.vstack(embeddings)
        return embeddings

def load_recommender(recommender, path, start_page=1):
    texts = pdf_to_text(path, start_page=start_page)
    chunks = text_to_chunks(texts, start_page=start_page)
    recommender.fit(chunks)
    return 'Corpus Loaded.'

def generate_text(openAI_key, prompt, engine="text-davinci-003"):
    openai.api_key = openAI_key
    completions = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=512,
        n=1,
        stop=None,
        temperature=0.7,
    )
    message = completions.choices[0].text.strip()
    return message

def generate_answer(recommender, question, instructions, openai_key):
    topn_chunks = recommender(question)
    prompt = ""
    prompt += 'Search results:\n\n'
    for c in topn_chunks:
        prompt += c + '\n\n'
        
    prompt += instructions + "\n"
    prompt += f"Query: {question}\nAnswer:"
    answer = generate_text(openai_key, prompt,"text-davinci-003")
    return answer

def start_processing():
    question = question_entry.get()
    instructions = instructions_entry.get()
    process_thread = threading.Thread(target=process, args=(question, instructions))
    process_thread.start()  

def question_answer(recommender, file, question, instructions, openAI_key):
    if openAI_key.strip()=='':
        return '[ERROR]: Please enter you Open AI Key. Get your key here : https://platform.openai.com/account/api-keys'
    
    if file is None:
        return '[ERROR]: No file provided. Please provide a PDF file.'

    old_file_name = file.name
    file_name = old_file_name[:-12] + old_file_name[-4:]
    os.rename(old_file_name, file_name)
    load_recommender(recommender, file_name)

    if question.strip() == '':
        return '[ERROR]: Question field is empty'

    return generate_answer(recommender, question, instructions, openAI_key)

def remove_bracketed_numbers(text):
    return re.sub(r'\[\d+\]', '', text)
