import os
import time
import faiss
import uuid

from openai import OpenAI
import gradio as gr
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

# from langchain import OpenAI, CoversationChain, LLMChain
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.storage import InMemoryStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import UnstructuredPDFLoader

import base64
import io

import fitz
from langchain_core.messages import HumanMessage
from PIL import Image
# from IPython.display import Image as IPImage
# from IPython.display import display


from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv()) # read local .env file

OPENAI_MODEL=os.environ.get("OPENAI_MODEL") # gpt-4o-mini
print("model: {}".format(OPENAI_MODEL))

retriever = ""
pages = []

def create_multi_vector_retriever(
    vectorstore, image_summaries, images
):
    """
    Create retriever that indexes summaries, but returns raw images or texts
    """

    # Initialize the storage layer
    store = InMemoryStore()
    id_key = "doc_id"

    # Create the multi-vector retriever
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=store,
        id_key=id_key,
    )

    # Helper function to add documents to the vectorstore and docstore
    def add_documents(retriever, doc_summaries, doc_contents):
        doc_ids = [str(uuid.uuid4()) for _ in doc_contents]
        summary_docs = [
            Document(page_content=s, metadata={id_key: doc_ids[i]})
            for i, s in enumerate(doc_summaries)
        ]
        retriever.vectorstore.add_documents(summary_docs)
        retriever.docstore.mset(list(zip(doc_ids, doc_contents)))

    # Check that image_summaries is not empty before adding
    if image_summaries:
        add_documents(retriever, image_summaries, images)

    return retriever


# The vectorstore to use to index the summaries
vectorstore = Chroma(
    collection_name="mm_rag_cj_blog", embedding_function=OpenAIEmbeddings()
)

# Create retriever
retriever_multi_vector_img = create_multi_vector_retriever(
    vectorstore,
    image_summaries,
    img_base64_list,
)


def img_prompt_func(pages):
    """
    Join the context into a single string
    """

    messages = []

    # Adding image(s) to the messages if present
    for image in pages:
        image_message = {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image}"},
        }
    messages.append(image_message)

    return [HumanMessage(content=messages)]

def image_summarize(img_base64, prompt):
    """Make image summary"""
    chat = ChatOpenAI(model="gpt-4-vision-preview", max_tokens=1024)

    msg = chat.invoke(
        [
            HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                    },
                ]
            )
        ]
    )
    return msg.content

def generate_img_summaries(path):
    """
    Generate summaries and base64 encoded strings for images
    path: Path to list of .jpg files extracted by Unstructured
    """

    # Store base64 encoded images
    img_base64_list = []

    # Store image summaries
    image_summaries = []

    # Prompt
    prompt = """You are an assistant tasked with summarizing images for retrieval. \
    These summaries will be embedded and used to retrieve the raw image. \
    Give a concise summary of the image that is well optimized for retrieval."""

    # Apply to images
    for img_file in sorted(os.listdir(path)):
        if img_file.endswith(".jpg"):
            img_path = os.path.join(path, img_file)
            base64_image = encode_image(img_path)
            img_base64_list.append(base64_image)
            image_summaries.append(image_summarize(base64_image, prompt))

    return img_base64_list, image_summaries

# Image summaries
img_base64_list, image_summaries = generate_img_summaries(fpath)    

def ask_ai(text, pages):
    _ = load_dotenv(find_dotenv()) # read local .env file

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



    response = model.invoke([message])
    print(response.content)

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

def pdf_page_to_base64(pdf_document, page_number: int):
    page = pdf_document.load_page(page_number)  # input is one-indexed
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")
       
def load_pdfContent(filename):
    doc = fitz.open(filename)
    pages = []

    for i in len(doc):
        pages.add(pdf_page_to_base64(doc, i)) 

    '''
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
        
    
            for pageNum,imgBlob in enumerate(pages):
                text = pytesseract.image_to_string(imgBlob,lang='eng')

                with open(f'PDF_page.txt', 'w') as the_file:
                    the_file.write(text)
   
        except Exception as e:
            print(e)
    '''

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

