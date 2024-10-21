import os
import time
import subprocess
import gradio as gr
import csv
import pandas as pd
from openai import OpenAI
from fdfgen import forge_fdf
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

OPENAI_MODEL=os.environ.get("OPENAI_MODEL")
print("model: {}".format(OPENAI_MODEL))

assert OPENAI_MODEL is not None and OPENAI_MODEL != '', 'Please define OPENAI_MODEL'
# OPENAI_MODEL='gpt-4'

# Set the option to display all rows
pd.set_option('display.max_rows', None)

mod_path = Path(__file__).parent
related_path="temp\pdftext.txt"
related_path2="temp\data.fdf"
src_path_1 = str((mod_path / related_path).resolve())
src_path_2 = str((mod_path / related_path2).resolve())

######
### PDF toolkit
######
def extract_text(pdf_filename):
    print("fn", src_path_1)
    pdftk_cmd = f"pdftotext {pdf_filename} "+ str(src_path_1)
    run_command(pdftk_cmd)
    return load_text_from_file(str(src_path_1))


def extract_fields(pdf_filename):
    pdftk_cmd = f"pdftk {pdf_filename} dump_data_fields output " + src_path_1 
    run_command(pdftk_cmd)
    return load_text_from_file(src_path_1)


######
### Text files
######
def load_text_from_file(filename):
    with open(filename) as f:
        text = f.read()
    return text


######
### OS commands
######
def run_command(cmd):
    print('run_command: starts')
    print(f'   running command: "{cmd}"')
    print(os.path.dirname(__file__))
    subprocess.run(cmd.split(), shell=True)


######
### Open AI gpt
######
def ask_ai(prompt, text):
    _ = load_dotenv(find_dotenv()) # read local .env file
    client = OpenAI()

    print('ask_ai: starts')
    print('   prompt:', prompt)

    completion = client.chat.completions.create(
      model=OPENAI_MODEL,
      messages=[
        {"role": "system", "content": f"""

        {prompt}

        """},
        {"role": "user", "content": f"""
        Text:

        {text}
        """}
        ]
    )

    return completion.choices[0].message.content if len(completion.choices) > 0 else None


######
### Data handling
######
def translate_string_to_tuples(input_string):

    l = []
    
    for i, s in enumerate(input_string.split('\n')):

        if i == 0: continue

        fv = s.replace('"','').replace('Field: ','').split(',')
        if len(fv) >= 2:
            value = ','.join(fv[1:])
            value = value.strip()
            l.append((fv[0], value))

    return l


######
### Chat interface
######
def print_like_dislike(x: gr.LikeData):
    print(x.index, x.value, x.liked)


def add_text(history, text):
    print('add_text: starts')
    print('   text:', text)
    history = history + [(text, None)]
    return history, gr.Textbox(value="", interactive=False)


def add_file(history, file):
    history = history + [((file.name,), None)]
    return history


def is_pdf_file(history):
    line = history[len(history)-1]
    line_part = line[0]
    print('   line_part:', line_part, type(line_part))
    if type(line_part) is tuple and '\Temp' in line_part[0] and '.pdf' in line_part[0]:
        return True


def original_filename(history):
    for line in history:
        line_part = line[0]
        print('type', type(line_part))
        print(line_part[0])
        print('temp', '\Temp' in line_part[0])
        print('pdf', '.pdf' in line_part[0])
        if type(line_part) is tuple and '\Temp' in line_part[0] and '.pdf' in line_part[0]:
            file = line_part[0]
            print(" file1: ", file)
            return file


def bot(history):
    print('bot: starts')
    print('   history12:', history)
    text = history[len(history)-1][0]

    if text == 'preview':

        response = None
        
        file = original_filename(history)
        print('   file:', file)

        if file is None:
            response = '**Preview command not available**'
        else:
            url = f'http://localhost:8000/file={file}'
            response = url

        print('   response:', response)
    elif is_pdf_file(history):
        response = 'Congratulations, you have uploaded a PDF file\nPlease enter your personal info.\n\n**info: (your personal info)**'

    else:

        pdf_filename = original_filename(history)

        pdf_text = extract_text(pdf_filename)
        print('   pdf_text:', pdf_text)

        # sanitize text
        prompt = """
        Please sanitize the text using these rules:
        - Format dates as MM/DD/YYYY
        - Format names as Last name, First name
        - Correct grammatical errors
        - Correct syntactical errors
        - Correct typos
        - Format amounts
        """

        input_text = f"""
        Text:
        {text}
        """

        sanitized_text = ask_ai(prompt, input_text)

        # ask ai to assign form values
        pdf_fields = extract_fields(pdf_filename)
        print('   pdf_fields:', pdf_fields)

        prompt = f"""
        You are assisting the user to fill a form.

        The form has these instructions...

        ############### INSTRUCTIONS: START
        {pdf_text}
        ############### INSTRUCTIONS: END

        The form has multiple fields defined next. 

        This is the form definition...

        {pdf_fields}

        Instructions for openai assistant:
        - Each field lives between --- blocks of characters
        - Analyse the input text and then find the best response to each field
        - If you don't find a valid response just return empty string instead of "Data not provided" or similar
        - Use the FieldNameAlt attribute to get the answer provided in the Answers provided by the user.
        - When you are asked to print output, use FieldName attribute instead of the FieldNameAlt attribute
        - The FieldType indicates if the field is Text, Button or other types.

        IMPORTANT: FieldName attribute must be printed and FieldNameAlt is ignored when you output your response.

        Response must be formatted in CSV format using FieldName and the best value you found.

        FieldName,Response

        """

        input_text = f"""
        Text:
        {sanitized_text}
        """

        filled_fields = ask_ai(prompt, input_text)

        # output directory
        output_dirname = os.path.dirname(original_filename(history))

        # Cleaning data
        filled_fields = filled_fields.replace('Data not provided', '')
        filled_fields = filled_fields.replace('DATA NOT PROVIDED', '')
        filled_fields = filled_fields.replace('Not provided', '')

        # fill fields by translating the string into a list of tuples
        fields = translate_string_to_tuples(filled_fields)

        # save filled fields
        output_filled_fields_filename = os.path.join(output_dirname, 'my-filled-fields.txt')
        if not os.path.exists(output_filled_fields_filename):
            # Convert the list of tuples to a DataFrame
            df = pd.DataFrame(fields, columns=['FieldName','Response'])

            # Save the DataFrame to a CSV file
            df.to_csv(output_filled_fields_filename, index=False)

        else:
            # Load existing values
            df = pd.read_csv(output_filled_fields_filename)
            df.set_index('FieldName', inplace = True)
            print('df')
            print(df)

            # Convert the list of tuples to a DataFrame
            df2 = pd.DataFrame(fields, columns=['FieldName','Response'])
            df2.set_index('FieldName', inplace = True)
            print('df2')
            print(df2)

            # Modify in place using non-NA values from another DataFrame.
            print('updating df')
            df.update(df2)

            '''
            # Append df2 to df1 along the rows (axis=0)
            df = pd.concat([df2, df], ignore_index=True)
            '''

            # Remove index not needed anymore
            df = df.reset_index()

            # Save the DataFrame to a CSV file
            df.to_csv(output_filled_fields_filename, index=False)

            # Convert DataFrame to a list of tuples
            fields = list(df.to_records(index=False))
            print('fields')
            print(fields)

        print('df')
        print(df)

        '''
        view_cmd = f"cat {output_filled_fields_filename}"
        print('view_cmd:', view_cmd)
        subprocess.run(view_cmd.split())
        exit('bye')
        '''

        # save fields to fdf
        fdf = forge_fdf("",fields,[],[],[])

        # create a form definition fields to burn field values into pdf file
        with open(src_path_2, "wb") as fdf_file:
            fdf_file.write(fdf)

        # save output

        output_pdf_filename = os.path.join(output_dirname, 'my-filled-form.pdf')

        print('-'*40)
        print('updating file: ', {output_pdf_filename})
        print('-'*40)
        pdftk_cmd = f"pdftk {pdf_filename} fill_form {src_path_2} output {output_pdf_filename}"
        subprocess.run(pdftk_cmd.split())

        # response with a link to preview
        response = f'Here is a preview of your filled form...\n\nhttp://localhost:8000/file={output_pdf_filename} \nPlease right-click and then select to Open in new tab.'

    history[-1][1] = ""
    for character in response:
        history[-1][1] += character
        time.sleep(0.05)
        yield history


with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        bubble_full_width=False,
        avatar_images=(None, (os.path.join(os.path.dirname(__file__), "avatar.png"))),
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text and press enter, or upload a PDF file.",
            container=False,
        )
        btn = gr.UploadButton("📁", file_types=[".pdf"])

    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
        bot, chatbot, chatbot, api_name="bot_response"
    )
    txt_msg.then(lambda: gr.Textbox(interactive=True), None, [txt], queue=False)
    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot, chatbot, chatbot
    )

    chatbot.like(print_like_dislike, None, None)


demo.queue()
demo.launch(server_name="127.0.0.1", server_port=8000)
