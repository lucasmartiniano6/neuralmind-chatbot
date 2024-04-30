# RAG based chatbot - Vestibular Unicamp
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from dotenv import load_dotenv
import os
import streamlit as st

def main():
    # load_dotenv() # load api-key from .env file
    
    filename = "./output.txt" # fonte de conhecimento confiável (gerado do site da PG-Unicamp, olhe ./fetch.py para mais info)
    txt = open(filename,"r").read()

    # separa o texto em blocos com overlap
    txt_format = CharacterTextSplitter( # (900,250) foi o que funcionou melhor entre os evals testados
        separator="\n",
        chunk_size=900,
        chunk_overlap=200,
        length_function=len
    )
    blocos = txt_format.split_text(txt)

    # cria a fonte de conhecimento confiável usando os blocos e os embeddings da OpenAI
    baseline = FAISS.from_texts(blocos, OpenAIEmbeddings())
    
    # caso a sessão de conversa não tenha sido iniciada, inicie com string vazia ""
    if 'conversation' not in st.session_state:
        st.session_state.conversation = ""

    st.title('Chatbot Vestibular da Unicamp')
    pergunta = st.text_input("Faça sua pergunta:")

    if pergunta:
        busca = baseline.similarity_search(pergunta) # busca a pergunta na fonte de conhecimento (Retrieval)
        ch = load_qa_chain(OpenAI(model="gpt-3.5-turbo-instruct"), chain_type="stuff") # usa a API do GPT-3.5 para gerar a resposta
        generated = ch.run(input_documents=busca, question=pergunta).strip() # Gerador
        st.session_state.conversation = generated # Guarde a resposta da sessão
        #print('Pergunta:', pergunta)
        #print('Resposta:', generated)

    st.text_area(label='Resposta:',value=st.session_state.conversation, height=200)

    image_url = 'https://upload.wikimedia.org/wikipedia/pt/thumb/b/b2/UNICAMP_logo.svg/1932px-UNICAMP_logo.svg.png'    
    st.image(image_url, width=250) # logo da unicamp

if __name__ == '__main__':
    if 'auth' not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.header("API Key Auth")
        api_key = st.text_input("Digite sua API key:", type="password")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key 
            st.session_state.auth = True
            st.experimental_rerun()
    else:
        main()
