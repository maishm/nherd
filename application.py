import pandas as pd
import numpy as np
import os
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import operator
from jinja2 import Environment, FileSystemLoader
import streamlit.components.v1 as components
from streamlit_metrics import metric, metric_row
from streamlit_echarts import st_echarts
# from bert_qa import bert_qa, load_qa_model, bert_summarization, load_summarization_model

# Use the full page instead of a narrow central column
st.set_page_config(layout="centered")
df = pd.read_csv('data/stock_data.csv')

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)    

def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)
    
def get_chunk(content,size):
        for i in range(0,len(content),size):
            yield content[i:i+size]

local_css("style.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')


st.sidebar.image('assets/logo.png', use_column_width=True)
stock_selection = st.sidebar.selectbox('Select a Stock', options=[" ", 'AIRASIA', 'GENM', 'NESTLE', 'GLOVE'], )
st.sidebar.checkbox("📈 Beginner", True)

if stock_selection == " ":
    with open('assets/animation.json') as json_file:
        lottie_data = json_file.read()
    loop = True
    env = Environment(loader = FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('template.html.jinja')
    st.title("Hello, Welcome! 👋")
    st.markdown("## This is where you will find the most reliable information on Malaysian stocks from reputable sources, verified and aggregated - *all in one place.*", unsafe_allow_html=True)
    html_data = template.render(data=lottie_data, loop=str(loop).lower())
    components.html(html_data, height=600)
    st.markdown("""
    <hr class="rounded">
    """, unsafe_allow_html=True)
    faq = st.beta_expander('Frequently Asked Questions')
    
    
else:
    df = df[df['stock'] == stock_selection]
    st.markdown(f"# *What* are Experts Saying About {stock_selection}?", unsafe_allow_html=True)
    st.markdown('<hr class="rounded">', unsafe_allow_html=True)
    overview = st.sidebar.beta_expander('Key Indicators')
    overview.markdown("""<p><b>Current Price</b> : RM 0.765 🟢 </p> \n <p><b>EPS</b> : - 0.950 🔻 </p> \n <p><b>Market Cap</b>: 2.56B  </p>""", unsafe_allow_html=True)
    


    stats = ({'Buy' : df['buy'].sum(), 
     'Sell' : df['sell'].sum(), 
     'Hold' : df['neutral'].sum()})
    
    max_percentage = max(stats.items(), key=operator.itemgetter(1))[1]/(sum(stats.values())) *100

    def generated_filtered_data(df, platform):
        filtered = df[df['platform'].isin(platform)]
        return [{'name' : 'Buy', 'value' : f"{filtered['buy'].sum()}"}, 
        {'name' : 'Sell', 'value' : f"{filtered['sell'].sum()}"}, 
        {'name' : 'Hold', 'value' : f"{filtered['neutral'].sum()}"}]
        
    
    def generate_pie_options(platform, data, color, maximum):
        pie_options = {
        "backgroundColor": "#EDF7F4",
        "title": {
            "text": f"{platform}",
            "left": "center",
            "top": 20,
            "textStyle": {"color": "#020202"},
        },
        "tooltip": {"trigger": "item", "formatter": "{a} <br/>{b} : {c} ({d}%)"},
        "visualMap": {
            "show": False,
            "min": 0,
            "max": maximum,
            "inRange": {"colorLightness": [0, 1]},
        },
        "series": [
            {
                "name": "Number of Analysts",
                "type": "pie",
                "radius": "55%",
                "center": ["50%", "50%"],
                "data": data,
                "roseType": "radius",
                "label": {"color": "020202"},
                "labelLine": {
                    "lineStyle": {"color": "020202"},
                    "smooth": 0.2,
                    "length": 10,
                    "length2": 20,
                },
                "itemStyle": {
                    "color": color,
                },
                "animationType": "scale",
                "animationEasing": "elasticOut",
            }
            ]}
        return pie_options
    
    st_echarts(options=generate_pie_options('Aggregated', generated_filtered_data(df, ['trading_view', 'investing', 'bursamktplace', 'reuters', 'wsj']), '#1e944f', 60))
    
    metric_row(
        {
            "Majority Verdict": max(stats.items(), key=operator.itemgetter(1))[0],
            "Majority Percentage": f'{round(max_percentage)}%',
            "Total Buy": df['buy'].sum(),
            "Total Sell": df['sell'].sum(),
            "Total Hold": df['neutral'].sum(),
        }   )
    
    def generate_table(df, platform):
        df = df[df['platform'] == platform ].reset_index()
        st.markdown(f"""
        <p><center> <b>Total Buy</b> : {df['buy'].sum()} </center></p> 
        <p><center> <b>Total Sell</b> : {df['sell'].sum()} </center></p> 
        <p><center> <b>Total Hold</b> : {df['neutral'].sum()} </center></p> 
        <p><center> <b>Link</b> : <a href={df['link'][0]}> Click here to view details. </a> </center></p> 
        <hr class="rounded">
                    """, unsafe_allow_html=True)
    c1, c2 = st.beta_columns((1, 1))

    with c1: st_echarts(options=generate_pie_options('Trading View', generated_filtered_data(df, ['trading_view']), '#418ce2', 20))
    with c1: generate_table(df, 'trading_view')

    with c2: st_echarts(options=generate_pie_options('Reuters', generated_filtered_data(df, ['reuters']), '#e2b741',20))
    with c2: generate_table(df, 'reuters')
    
    c3, c4 = st.beta_columns((1, 1))
    
    with c3: st_echarts(options=generate_pie_options('Investing.com', generated_filtered_data(df, ['investing']), '#EDF7F4',20))
    with c3: generate_table(df, 'investing')

    with c4: st_echarts(options=generate_pie_options('Bursa Market Place', generated_filtered_data(df, ['bursamktplace']), '#e25941',20))
    with c4: generate_table(df, 'bursamktplace')


    st_echarts(options=generate_pie_options('WSJ', generated_filtered_data(df, ['wsj']), '#323234', 20))
    generate_table(df, 'wsj')

    
    st.markdown("""# *Why* are Experts Suggesting this? \n Looking into the various analyst reports is the most credible way to understand this. So we condense these reports using Machine Learning & NLP. """, unsafe_allow_html=True)

    arr = os.listdir(f'data/{stock_selection}')
    arr.remove('summary')
    arr.remove('answer')
    
    rr = st.beta_expander('Research Reports')
    summary_checkbox = rr.checkbox('Summarize', False)
    research_report = rr.selectbox("Select a Report", options=[a.replace(".txt", "") for a in arr])
    
    with open(f"data/{stock_selection}/{research_report}.txt", encoding='cp1252') as f: 
       text = f.read()
    
    if summary_checkbox:
        try:
            with open(f"data/{stock_selection}/summary/{research_report}.txt", encoding='cp1252') as f: 
                summary = f.read()
            st.markdown(f"### Summary: \n {summary}")
        except:
            rr.warning("Oops, try again.")
            # summarization = load_summarization_model()
            # bert_summarization(summarization, text)
    else:
        question = rr.text_input("Ask any question on the report")
        if question != "": 
            try:
                with open(f"data/{stock_selection}/answer/answer.txt", encoding='cp1252') as f: 
                    answer = f.read()
                    answer = answer.splitlines()
                for a in answer:    
                    st.markdown(f"### {a}")
            except:
                rr.warning("Oops, try again.")
                # with st.spinner('Digesting the report..'):
                #     model, tokenizer = load_qa_model()
                #     answers = bert_qa(model, tokenizer, text, question)
            
                # cleaned_answers = [ans for ans in answers if len(ans) > 12 and "?" not in ans]

                # for ans in cleaned_answers:
                #     st.markdown(f"## • {ans.capitalize()}") 
        else: 
            rr.warning("Type in your question")
                
        
    
        