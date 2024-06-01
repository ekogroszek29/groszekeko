from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas as pd 
from newspaper import Article, Config
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification,pipeline,BertTokenizer, BertForSequenceClassification
from deta import Deta
import datetime
from transformers import AutoTokenizer, AutoModelForTokenClassification
import nltk
nltk.download('punkt')
from deep_translator import GoogleTranslator


DETA_KEY = 'a0h9yczcu4i_qK79MPnawKRHY5HmMDT2yqpxaRQFd65s'
deta = Deta(DETA_KEY)
db = deta.Base("Wegry")

today_1 = datetime.datetime.today()
today = today_1.strftime('%Y-%m-%d')

#załadowanie danych do bazy
def insert_period(key,title,summary,keywords,text,url,ass,today):
    return db.put({"key": key, "title":title,"summary":summary,
                   "keywords":keywords,"text":text,"url":url,"ass":ass,"today":today})

#keywords
tokenizer_key = AutoTokenizer.from_pretrained("Jean-Baptiste/roberta-large-ner-english")
model_key = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/roberta-large-ner-english")
nlp = pipeline('ner', model=model_key, tokenizer=tokenizer_key, aggregation_strategy="simple")

#summarization
summarizer = pipeline("summarization", model="philschmid/bart-large-cnn-samsum")

#Sentiment Analysis
finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone',num_labels=3)
tokenizer_sen = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
sena = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer_sen)

###########################
###                   WEGRY
###########################

def check_string_after_gazdasag(url):
    search_string = "gazdasag/"
    if search_string in url:
        index = url.index(search_string) + len(search_string)
        return url[index:index + 2] == "20"
    return False

try:
    hu_portfolio = []

    for j in range(1,3):
        req = Request(f"https://www.portfolio.hu/gazdasag?page={j}")
        html_page = urlopen(req)

        soup = BeautifulSoup(html_page, "lxml")



        links_portfolio = []
        for link in soup.findAll('a'):
            if "gazdasag" in link.get('href') and check_string_after_gazdasag(link.get('href')) and link.get('href')[:4] == 'http' :
                x = link.get('href')
                links_portfolio.append(x)

        links_portfolio = list(dict.fromkeys(links_portfolio))

        for i in links_portfolio:
            article = Article(i)
            article.download()
            article.parse()
            article.nlp()

            #Tłumaczenie
            article_en = ""
            for a in range(0,len(article.text),1800):
                input_ids = tokenizer(article.text[a:a+1800], return_tensors="pt").input_ids
                outputs = model.generate(input_ids=input_ids, num_beams=5, num_return_sequences=1)
                article_en_tmp= tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
                article_en += article_en_tmp

            #tytul
            input_ids = tokenizer(article.title, return_tensors="pt").input_ids
            outputs = model.generate(input_ids=input_ids, num_beams=5, num_return_sequences=1)
            article_title= tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

            #keywords
            article_keywords = nlp(article_en[:4000])
            article_keywords = [article_keywords[i]['word'] for i in range(len(article_keywords)) ]
            article_keywords = list(dict.fromkeys(article_keywords))

            #summarization
            article_summary_en = summarizer(article_en[:4000], max_length=230, min_length=50, do_sample=False)
            art_tmp = article_summary_en[0]['summary_text']
            article_summary = ""
            for a in range(0,len(art_tmp),1500):
                input_ids = tokenizer_pl(art_tmp[a:a+1500], return_tensors="pt").input_ids
                outputs = model_pl.generate(input_ids=input_ids, num_beams=5, num_return_sequences=1, max_new_tokens=200)
                article_summ= tokenizer_pl.batch_decode(outputs, skip_special_tokens=True)[0]
                article_summary += article_summ

            #Sentiment Analysis
            article_ass = sena(article_en[:2000])[0]['label']

            hu_portfolio.append([
                    article_title
                    ,article_summary
                    ,article_keywords
                    ,article_en
                    ,article.url
                    ,article_ass])
    
    
    
    df = pd.DataFrame(hu_portfolio, columns =['title',"summary","keywords","text","url","sentiment_analysis"])
    
    
    title = df['title'].tolist()
    title = [str(x) for x in title]
     
    summary = df['summary'].tolist()
    summary = [str(x) for x in summary]
    
    keywords = df['keywords'].tolist()
    keywords = [str(x) for x in keywords]
    
    text = df['text'].tolist()
    text = [str(x) for x in text]
    
    url = df['url'].tolist()
    url = [str(x) for x in url]
    
    ass = df['sentiment_analysis'].tolist()
    ass = [str(x) for x in ass]
    
    key = today + '_hu_portfolio'
    
    insert_period(key,title,summary,keywords,text,url,ass,today)
except:
    print("Problem")


###########################
###                   Czechy
###########################

DETA_KEY = 'a0h9yczcu4i_qK79MPnawKRHY5HmMDT2yqpxaRQFd65s'
deta = Deta(DETA_KEY)
db = deta.Base("Czechy")



try:
    cz_idnes = []

    for j in range(1,3):
        req = Request("https://www.idnes.cz/ekonomika")
        html_page = urlopen(req)

        soup = BeautifulSoup(html_page, "lxml")
        links_dnes = []
        for link in soup.findAll('a'):
            x = str(link.get('href'))
            if x[:31] == 'https://www.idnes.cz/ekonomika/' and len(x)>100:
                links_dnes.append(x)

        links_idnes = list(dict.fromkeys(links_dnes))

        for i in links_idnes:
            article = Article(i)
            article.download()
            article.parse()
            article.nlp()

            #Tłumaczenie
            article_en = ""
            for a in range(0,len(article.text),1800):
                article_en_tmp = GoogleTranslator(source='cs', target='en').translate(article.text[a:a+1800])
                article_en += article_en_tmp

            #tytul
            article_title= GoogleTranslator(source='cs', target='en').translate(article.title)

            #keywords
            article_keywords = nlp(article_en[:4000])
            article_keywords = [article_keywords[i]['word'] for i in range(len(article_keywords)) ]
            article_keywords = list(dict.fromkeys(article_keywords))

            #summarization
            article_summary_en = summarizer(article_en[:4000], max_length=230, min_length=50, do_sample=False)
            art_tmp = article_summary_en[0]['summary_text']
            article_summary = ""
            for a in range(0,len(art_tmp),1500):
                input_ids = tokenizer_pl(art_tmp[a:a+1500], return_tensors="pt").input_ids
                outputs = model_pl.generate(input_ids=input_ids, num_beams=5, num_return_sequences=1, max_new_tokens=200)
                article_summ= tokenizer_pl.batch_decode(outputs, skip_special_tokens=True)[0]
                article_summary += article_summ

            #Sentiment Analysis
            article_ass = sena(article_en[:2000])[0]['label']

            cz_idnes.append([
                    article_title
                    ,article_summary
                    ,article_keywords
                    ,article_en
                    ,article.url
                    ,article_ass])
    
    
    
    df = pd.DataFrame(cz_idnes, columns =['title',"summary","keywords","text","url","sentiment_analysis"])
    
    
    title = df['title'].tolist()
    title = [str(x) for x in title]
     
    summary = df['summary'].tolist()
    summary = [str(x) for x in summary]
    
    keywords = df['keywords'].tolist()
    keywords = [str(x) for x in keywords]
    
    text = df['text'].tolist()
    text = [str(x) for x in text]
    
    url = df['url'].tolist()
    url = [str(x) for x in url]
    
    ass = df['sentiment_analysis'].tolist()
    ass = [str(x) for x in ass]
    
    key = today + '_hu_portfolio'
    
    insert_period(key,title,summary,keywords,text,url,ass,today)
except:
    print("Problem")





































