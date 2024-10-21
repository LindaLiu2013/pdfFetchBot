import os
import time
import faiss
from openai import OpenAI
import gradio as gr
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

# from langchain import OpenAI, CoversationChain, LLMChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory 
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import UnstructuredPDFLoader

from pdf2image import convert_from_path


from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv()) # read local .env file

OPENAI_MODEL=os.environ.get("OPENAI_MODEL")
print("model: {}".format(OPENAI_MODEL))

retriever = ""
pages = []

def define_retriever(pages):
    print('define retriever')
     # text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        # shows how to seperate
        separators=["\n\n", "\n", " ", ""],
        # Shows the document token length
        chunk_size=1000,
        # How much overlap should exist between documents
        chunk_overlap=200,
        # How to measure length
        length_function=len
        )

    # Applying the splitter
    docs = text_splitter.split_documents(pages)

    # uses OpenAI embeddings to build a retriever
    embeddings = OpenAIEmbeddings(api_key=os.environ.get("OPENAI_API_KEY"))

    # Creates the document retriever using docs and embeddings
    db = FAISS.from_documents(docs, embeddings)

    # Asking the retriever to do similarity search based on Query
    # answer = db.similarity_search(text)

    # Building the retriever
    return db.as_retriever(search_type="mmr", search_kwargs={'k': 6})
    

def ask_ai(text, retriever):
    _ = load_dotenv(find_dotenv()) # read local .env file
    # client = OpenAI()

    print('ask_ai: starts')
    
    # response = retriever.invoke(text)
    
    # Converts the prompt into a prompt template
    # This is the prompt used
    template = """
     You are a information retrieval AI. Format the retrieved information as a text
     Use only the context for your answers, do not make up information
     query: {query}
     {context} 
    """

    prompt_template = ChatPromptTemplate.from_template(template)
    print('prompt_template',  prompt_template)
  
    model = ChatOpenAI(api_key=os.environ.get("OPENAI_API_KEY"), model=OPENAI_MODEL)

    # Construction of the chain
    chain = (
     # The initial dictionary uses the retriever and user supplied query
      {"context": retriever,
     "query": RunnablePassthrough()}
     # Feeds that context and query into the prompt then model & lastly 
     # uses the ouput parser, do query for the data.
    |   prompt_template  | model | StrOutputParser()
    )

    response = chain.invoke(text)

    return response

    '''
    vector_store = InMemoryVectorStore.from_documents(pages, OpenAIEmbeddings())
    docs = vector_store.similarity_search(text, k=2)
    answers = []
    for doc in docs:
        print(f'Page {doc.metadata["page"]}: {doc.page_content[:300]}\n')
        answers.append(f'Page {doc.metadata["page"]}: {doc.page_content[:300]}\n')
    
        
    return  ''.join(answers) 

    '''

    '''
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
   '''
  
def add_text(history, text):
    print('add_text: starts')
    print('   text:', text)
    history = history + [(text, None)]
    return history, gr.Textbox(value="", interactive=False)


def is_pdf_file(history):
    line_part = history[len(history)-1][0]
    print('type1', type(line_part))
    if type(line_part) is tuple and '\Temp' in line_part[0] and '.pdf' in line_part[0]:
        return True

def add_file(history, file):
    history = history + [((file.name,), None)]
    return history  

def original_filename(history):
     for line in history:
        line_part = line[0]
        print('type', type(line_part))
        if type(line_part) is tuple and '\Temp' in line_part[0] and '.pdf' in line_part[0]:
            file = line_part[0]
            print(" file1: ", file)
            return file
       
def load_pdfContent(filename):
    loader = PyPDFLoader(filename)
    pages = loader.load_and_split()
      
    if len(pages) == 0:
        try:
            # pages = convert_from_path(filename, 500)
            loader = UnstructuredPDFLoader(
            file_path=filename,
            mode="elements",
            strategy="fast",
            )
            pages = loader.load()
        
            ''' 
            for pageNum,imgBlob in enumerate(pages):
                text = pytesseract.image_to_string(imgBlob,lang='eng')

                with open(f'PDF_page.txt', 'w') as the_file:
                    the_file.write(text)
            '''
        except Exception as e:
            print(e)
        
    return pages
     
def bot(history):
    print('bot: starts')
    print('   history12:', history)
    text = history[len(history)-1][0]

    if is_pdf_file(history):
        response = 'Congratulations, you have uploaded a PDF file\nPlease enter your question.\n\n**info: your question for the context in the PDF**'
    else:
        pdf_filename = original_filename(history)

        print('pdf file name: ', pdf_filename)
        
        if pdf_filename == None:
            response = "No pdf file upload. Please upload a file"
        else: 
            global pages
            if pages == []:
                pages = load_pdfContent(pdf_filename)

            if pages == None or len(pages) == 0:
                 response = "Not a valid pdf file. If it's a scanned PDF, please convert it to the click able PDF file firstly."
            else:     
                print(f"{pages[0].metadata}\n")
             
                input_text = f"""
                Text:
                {text}
                """

                global retriever

                if retriever == "":             
                    retriever = define_retriever(pages)

                response = ask_ai(input_text, retriever)
        
    print('response', response)
       
    history[-1][1] = ""
    history[-1][1] += response
    time.sleep(0.05)
    yield history

    print('history', history)

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


demo.queue()
demo.launch(server_name="127.0.0.1", server_port=8000)

