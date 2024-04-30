# RAG based chatbot - Vestibular Unicamp
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.evaluation import load_evaluator
from langchain.evaluation import EmbeddingDistance
from dotenv import load_dotenv

def distance(truth, prediction): # COSINE SIMILARITY
    """
        Cálcula a distância entre as strings usando os embeddings da OpenAI (normalizados de [0,1]). 
        Por padrão o evaluator usa cosine similarity, mas também é possível escolher entre distancia euclidiana,manhattan,hamming ou chebyshev
    """
    evaluator = load_evaluator("embedding_distance", distance_metric=EmbeddingDistance.COSINE) 
    dist = evaluator.evaluate_strings(prediction=prediction, reference=truth) # quanto mais perto de 0 mais similiar são as strings
    threshold = 0.001
    return dist['score'] if dist['score'] > threshold else 0.0

def main():
    load_dotenv() # load api-key
    
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
    
    accuracy = 0.0 # acuracia do chatbot

    teste = open("questions.txt","r").read() # lê o conteúdo do questionário
    teste = teste.split("\n") # separa na lista [pergunta+resposta]
    teste.pop() # último item é uma string vazia "", então removemos
    for item in teste: 
        item = item.split("?") 
        pergunta,resposta = item[0][10:], item[1][11:]
        busca = baseline.similarity_search(pergunta) # busca a pergunta na fonte de conhecimento (Retrieval)
        ch = load_qa_chain(OpenAI(model="gpt-3.5-turbo-instruct"), chain_type="stuff") # usa a API do GPT-3.5 para gerar a resposta
        generated = ch.run(input_documents=busca, question=pergunta).strip() # Gerador
        dist = distance(resposta, generated) # Calcula distância entre as strings (quanto MENOR dist. mais parecido são as strings)
        accuracy += (1-dist) # usamos acurácia quanto MAIOR mais parecido! (distância está normalizada [0,1])

        print("Pergunta:", pergunta)
        print("Resposta certa:", resposta)
        print("Resposta modelo:", generated)
        print("Dist:", dist,'\n')

    accuracy /= len(teste) 
    print('Acc final:', accuracy)
            
        
if __name__ == '__main__':
    main()
    #print(distance("white", "black"))