import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from gpt_pdf_processor import process_pdf_files
from data_to_excel import convert_to_excel
import threading

class ToolTip(object):
    def __init__(self, widget, text='Widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)

    def enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tw, text=self.text, background="#ffffff", relief='solid', borderwidth=1)
        label.pack(ipadx=1)

    def close(self, event=None):
        if self.tw:
            self.tw.destroy()

def update_status_label(current, total):
    status_label.config(text=f"Processing {current} out of {total} PDFs")

def browse_input_folder():
    input_folder = filedialog.askdirectory()
    input_folder_label.config(text=input_folder)

def browse_output_folder():
    output_folder = filedialog.askdirectory()
    output_folder_label.config(text=output_folder)

def process():
    process_button.config(state=tk.DISABLED)
    update_status_label("Starting...", "")
    input_folder = input_folder_label.cget('text')
    output_folder = output_folder_label.cget('text')
    openai_key = openai_key_entry.get("1.0", 'end-1c')
    question = question_text.get("1.0", tk.END)
    instructions = instructions_text.get("1.0", tk.END)  # This line gets the text from the instructions_text widget

    if not os.path.exists(input_folder):
        messagebox.showerror("Error", "Input folder does not exist.")
        return

    if not os.path.exists(output_folder):
        messagebox.showerror("Error", "Output folder does not exist.")
        return

    if not openai_key:
        messagebox.showerror("Error", "OpenAI key is required.")
        return

    if not question:
        messagebox.showerror("Error", "Question is required.")
        return

    process_pdf_files(input_folder, output_folder, question, instructions, openai_key, progress_callback=update_status_label)
    convert_to_excel(output_folder, output_folder)
    messagebox.showinfo("Success", "Processing completed.")
    process_button.config(state=tk.NORMAL)

def start_processing():
    process_thread = threading.Thread(target=process)
    process_thread.start()

app = tk.Tk()
app.title("PDF Processor")

input_folder_button = ttk.Button(app, text="Browse Input Folder", command=browse_input_folder)
input_folder_button.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
input_folder_label = ttk.Label(app, text="")
input_folder_label.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

output_folder_button = ttk.Button(app, text="Browse Output Folder", command=browse_output_folder)
output_folder_button.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
output_folder_label = ttk.Label(app, text="")
output_folder_label.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

openai_key_label = ttk.Label(app, text="OpenAI Key:")
openai_key_label.grid(row=2, column=0, padx=10, pady=10, sticky='ew')
openai_key_entry = tk.Text(app, height=2)
openai_key_entry.grid(row=2, column=1, padx=10, pady=10, sticky='ew')

question_label = ttk.Label(app, text="Question:")
question_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')  # use 'w' for left alignment
question_text = tk.Text(app, width=60, height=10)
question_text.grid(row=3, column=1, padx=10, pady=10, sticky='ew')

question_info = ttk.Button(app, text="?", width=2)
question_info.grid(row=3, column=2, padx=10, pady=10, sticky='w')  # use 'w' for left alignment
question_tooltip = ToolTip(question_info, "Enter a specific question here that GPT will answer based on the PDF content.")

instructions_label = ttk.Label(app, text="Instructions:")
instructions_label.grid(row=4, column=0, padx=10, pady=10, sticky='w')  # use 'w' for left alignment
instructions_text = tk.Text(app, height=5, width=50)
instructions_text.grid(row=4, column=1, padx=10, pady=10, sticky='ew')

instructions_info = ttk.Button(app, text="?", width=2)
instructions_info.grid(row=4, column=2, padx=10, pady=10, sticky='w')  # use 'w' for left alignment
instructions_tooltip = ToolTip(instructions_info, "Enter instructions for how GPT should process and structure the answer based on the PDF content.")

spacer_left = ttk.Label(app)
spacer_left.grid(row=5, column=0, columnspan=1, sticky='ew')
process_button = ttk.Button(app, text="Process Files", command=start_processing, width=20)  # Set width to a fixed value
process_button.grid(row=5, column=1, padx=10, pady=10)  # Removed sticky='ew' so button will not stretch
spacer_right = ttk.Label(app)
spacer_right.grid(row=5, column=2, columnspan=1, sticky='ew')

status_label = ttk.Label(app, text="")
status_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)  # spans across two columns

app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)
app.grid_columnconfigure(2, weight=1)

app.mainloop()