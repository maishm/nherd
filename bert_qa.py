#%% 
from streamlit import spinner
import torch
from transformers import BertForQuestionAnswering
from transformers import BertTokenizer
from transformers import pipeline
import streamlit as st

@st.cache(show_spinner=False)
def load_qa_model():
    model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    #Tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    return model, tokenizer

@st.cache(show_spinner=False)     
def bert_qa(model, tokenizer, text,question):
    
    def get_chunk(content,size):
            for i in range(0,len(content),size):
                yield content[i:i+size]
    answers = []
    for idx,val in enumerate(get_chunk(text, 1000)):
        paragraph = val         
        encoding = tokenizer.encode_plus(text=question,text_pair=paragraph, truncation=True)
        inputs = encoding['input_ids']  #Token embeddings
        sentence_embedding = encoding['token_type_ids']  #Segment embeddings
        tokens = tokenizer.convert_ids_to_tokens(inputs) #input tokens
        start_scores, end_scores = model(input_ids=torch.tensor([inputs]), token_type_ids=torch.tensor([sentence_embedding]))
        start_index = torch.argmax(start_scores)
        end_index = torch.argmax(end_scores)
        answer = ' '.join(tokens[start_index:end_index+1])
        corrected_answer = ''

        for word in answer.split():
            
            #If it's a subword token
            if word[0:2] == '##':
                corrected_answer += word[2:]
            else:
                corrected_answer += ' ' + word
        answers.append(corrected_answer)
    
    return answers


def load_summarization_model():
    summarization = pipeline("summarization")
    return summarization

def bert_summarization(summarization, original_text):
    def get_chunk(content,size):
        for i in range(0,len(content),size):
            yield content[i:i+size]
    for idx,val in enumerate(get_chunk(original_text, 1000)):
        original_text = str(val)
        summary_text = summarization(original_text)[0]['summary_text']
        st.markdown(f"### Summary {idx+1}: \n {summary_text}")
