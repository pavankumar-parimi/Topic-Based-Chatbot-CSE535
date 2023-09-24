from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import urllib.request
from urllib.parse import quote
import json
from sentence_transformers import SentenceTransformer
import numpy as np
import random
import os
import re
from nltk.corpus import stopwords
import pprint

app = Flask(__name__)
CORS(app)


@app.route("/query_reference", methods=["POST"])
def index():
    # Chitchat write implicit rules
    print("I am at this endpoint")
    query = request.get_json()["query"]
    topic = request.get_json()["topic"]

    if topic== "chitchat":
        """ Chit Chat inurl"""
        chitchat_inurl = "http://34.125.133.9:8983/solr/project_chitchat/select?defType=edismax&indent=true&pf=Question&q.op=OR&q="+quote("Question:"+query)+"&qf=Question"
        print("chit chat inurl:", chitchat_inurl)
    else:
        """Reddit Url"""
        reddit_inurl = "http://34.125.133.9:8983/solr/project_reddit_core/select?defType=edismax&indent=true&pf=parent_body&q.op=OR&q="+quote("parent_body:"+query)+"&qf=parent_body"
        print("reddit inurl:", reddit_inurl)

    return jsonify(msg="Looks Good")
    # If something doesn't matches chitchat send the query to reddit.
    # If result is from chitchat directly return the response.
    # else return the results fetched from core
    

@app.route("/query", methods = ["POST"])
def query():
    print("I am at query endpoint")

    data = request.get_json()
    user_query = data["message"]
    user_query = user_query.replace(':', '')

    label = classify_query(user_query)

    topics_list_dict = data["topics"]
    
    topics = []
    chitchat_docs = []
    reddit_docs = []

    chitchat_sentences = []
    chitchat_answer_question = {}

    reddit_sentences = []
    reddit_parent_body = {}

    for each in topics_list_dict:
        topics.append(each["item_text"])

    if label[0] == "chitchat":
        chitchat_inurl = "http://34.125.133.9:8983/solr/project_chitchat/select?defType=edismax&indent=true&pf=Question&q.op=OR&q="+quote("Question:"+user_query)+"&qf=Question"
        chitchatdata = urllib.request.urlopen(chitchat_inurl)
        chitchat_docs = json.load(chitchatdata)['response']['docs']

        for sentence in chitchat_docs:
            chitchat_sentences.append(sentence["Question"])
            if sentence["Question"][0] not in chitchat_answer_question:
                chitchat_answer_question[sentence["Question"][0]] = [sentence["Answer"][0]]
            else:
                chitchat_answer_question[sentence["Question"][0]].extend([sentence["Answer"][0]])

        # if chitchat_docs:
        #     print("************************************************************************************")
        #     print("------------------------------------------------------------------------------------")
        #     print("ChitChat Response:", chitchat_docs[0]["Answer"])
        #     print("------------------------------------------------------------------------------------")
        #     print("************************************************************************************")
    else:
        topic_len = len(topics)
        topic_query = ""
        # for topic in topics:
        #     topic_query += "topic:"+topic+"\n"
        start = 1
        while start < topic_len:
            topic_query += "topic:"+topics[start-1]+" "
            start+=1
        topic_query+="topic:"+topics[-1]
        
        # user_query = re.sub("[^A-Z]", " ", user_query,0,re.IGNORECASE).lower()

        # user_query_bag_of_words = []

        # for data in user_query.split(" "):
        #     if data not in set(stopwords.words("english")):
        #         user_query_bag_of_words.append(data)

        # print("************************************************************************************************************************************************************************")
        # print("User Bag Of Words:", user_query_bag_of_words)
        # print("************************************************************************************************************************************************************************")


        

        reddit_inurl = "http://34.125.133.9:8983/solr/project_reddit_core/select?defType=edismax&facet=true&facet.field=topic&fq="+quote(topic_query)+"&indent=true&pf=parent_body&q.op=OR&q="+quote("parent_body:"+" ".join(label[1]))+"&qf=parent_body"
        
        print("************************************************************************************************************************************************************************")
        print("Reddit URL:", reddit_inurl)
        print("************************************************************************************************************************************************************************")

        
        redditdata = urllib.request.urlopen(reddit_inurl)
        reddit_docs = json.load(redditdata)['response']['docs']

        

        for sentence in reddit_docs:
            print("Sentence:", sentence)
            if sentence.get('parent_body', None):
                reddit_sentences.append(sentence["parent_body"])
            if sentence["parent_body"] not in reddit_parent_body:
                reddit_parent_body[sentence["parent_body"]] = [sentence.get("body", None)]
            else:
                reddit_parent_body[sentence["parent_body"]].extend([sentence.get("body", None)])

        # if reddit_docs:
        #     print()
        #     print()

        #     print("************************************************************************************")
        #     print("------------------------------------------------------------------------------------")
        #     print("Reddit Response:", reddit_docs[0]["body"])
        #     print("------------------------------------------------------------------------------------")
        #     print("************************************************************************************")


    sentences = []
    if label[0]== "reddit":
        sentences.extend(chitchat_sentences)
    else:
        sentences.extend(reddit_sentences)
    
    model = SentenceTransformer('bert-base-nli-mean-tokens')

    embeddings = model.encode(sentences)

    query_vec = model.encode([user_query])[0]

    # return_sentence1 = ""
    # return_sentence2 = ""
    # max_sim1 = 0
    # max_sim2 = 0

    return_sentence = ""
    max_sim = 0

    if label[0] == "chitchat":
        for sent in chitchat_sentences:
            sim = cosine(query_vec, model.encode([sent[0]])[0])
            if sim > max_sim:
                max_sim = sim
                return_sentence = sent
            print("Sentence = ", sent, "; similarity = ", sim)

        # print()
        # print()

        # print("************************************************************************************************************************************************************************")
        # print("CHIT-CHAT")
        # print("************************************************************************************************************************************************************************")

        # print()
        # print()

        # print("************************************************************************************")
        # print("------------------------------------------------------------------------------------")
        # print("Query Response:", return_sentence)
        # print("------------------------------------------------------------------------------------")
        # print("************************************************************************************")
    else:
        for sent in reddit_sentences:
            sim = cosine(query_vec, model.encode([sent[0]])[0])
            if sim > max_sim:
                max_sim = sim
                return_sentence = sent
            print("Sentence = ", sent, "; similarity = ", sim)


        # print()
        # print()

        # print("************************************************************************************************************************************************************************")
        # print("REDDIT")
        # print("************************************************************************************************************************************************************************")

        # print()
        # print()

        # print("************************************************************************************")
        # print("------------------------------------------------------------------------------------")
        # print("Query Response:", return_sentence)
        # print("------------------------------------------------------------------------------------")
        # print("************************************************************************************")

    

    # print("************************************************************************************************************************************************************************")
    # print("Return Sentence 1:", return_sentence1)
    # print("************************************************************************************************************************************************************************")
    # print("Return Sentence 2:", return_sentence2)
    # print("************************************************************************************************************************************************************************")

    # if max_sim1 > max_sim2:
    #     print(chitchat_answer_question[return_sentence1[0]])
    #     len_chit_chat_answer_question = len(chitchat_answer_question[return_sentence1[0]])
    #     if len_chit_chat_answer_question <= 1:
    #         return_sentence = chitchat_answer_question[return_sentence1[0]][len_chit_chat_answer_question-1]
    #     else:
    #         return_sentence = chitchat_answer_question[return_sentence1[0]][random.choice(list(range(len_chit_chat_answer_question-1)))]
    # else:
    #     if return_sentence2:
    #         return_sentence = reddit_parent_body[return_sentence2]

    # if chitchat_docs or reddit_docs:
    #     if len(return_sentence) > 0:
    #         print("Docs returned.")
    #         return jsonify(msg = return_sentence)
    #     else:
    #         print("Zero Docs returned.")
    #         return jsonify(msg = "")
    # else:
    #     print("Zero Docs returned.")
    #     return jsonify(msg = "")

    if chitchat_docs or reddit_docs:
        if label[0] == "chitchat":
            if len(return_sentence) > 0:
                print("Docs Returned.")
                len_chit_chat_answer_question = len(chitchat_answer_question[return_sentence[0]])
                print(chitchat_answer_question[random.choice(return_sentence)])
                final_sentence = ''
                if len_chit_chat_answer_question <= 1:
                    final_sentence = chitchat_answer_question[return_sentence[0]][len_chit_chat_answer_question-1]
                else:
                    final_sentence = chitchat_answer_question[return_sentence[0]][random.choice(list(range(len_chit_chat_answer_question-1)))]

                return jsonify(msg = {"msg":final_sentence, "type":"chitchat"})
            else:
                print("Zero Docs Returned.")
                return jsonify(msg = {"msg": final_sentence, "type":"chitchat"})
        else:
            if len(return_sentence) > 0:
                print("Docs Returned.")
                print(reddit_parent_body)
                return jsonify(msg = {"msg":reddit_parent_body[return_sentence], "type":"reddit"})
            else:
                print("Zero Docs Returned.")
                return jsonify(msg = {"msg":"", "type":"reddit"})
    else:
        print("Zero Docs Returned.")
        return jsonify(msg = {"msg":"", "type":"chitchat"})


def cosine(u, v):
    return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))


def classify_query(user_query):
    with open('sample.json') as json_file:
        data = json.load(json_file)

        sentence = re.sub("[^A-Z]", " ", user_query,0,re.IGNORECASE).lower()
        sentence_len = len(sentence.split(" "))
        count = 0
        words_not_in_Bag_of_Words = []
        for word in sentence.split(" "):
            print("User Word:",word)
            print("Check in Model:", data.get(word, None))
            if data.get(word, None):
                count += 1
            else:
                words_not_in_Bag_of_Words.append(word)

        print("************************************************************************************************************************************************************************")
        print("Sentence Length:", sentence_len)
        print("************************************************************************************************************************************************************************")
        print("Count:", count)
        print("************************************************************************************************************************************************************************")
        print("Threshold:", count/sentence_len)
        print("************************************************************************************************************************************************************************")
        
        if (count / sentence_len) > 0.85:
            return "chitchat", words_not_in_Bag_of_Words
        else:
            print("************************************************************************************************************************************************************************")
            print("Words Not in Bag Of Words:",words_not_in_Bag_of_Words)
            print("************************************************************************************************************************************************************************")
            return "reddit", words_not_in_Bag_of_Words


@app.route("/visualize", methods = ["POST"])
def visualize():
    topics = request.get_json()["topics"]
    msg = request.get_json()["message"]
    type = request.get_json()["type"]
    print("Topics:", topics)
    print("Msg:", msg)
    print("type:", type)
    topic_based_relevance = {
        "Politics":{
            "Relevant":0,
            "Irrelevant":0
            },
        "Education":{
            "Relevant":0,
            "Irrelevant":0
            },
        "HealthCare":{
            "Relevant":0, 
            "Irrelevant":0
            }, 
        "Technology":{
            "Relevant":0, 
            "Irrelevant":0
            }, 
        "Environment":{
            "Relevant":0, 
            "Irrelevant":0
            }
        }
    if type == "reddit":
        relevant_irrelevant_map = {"Relevant":"Irrelevant", "Irrelevant":"Relevant"}
        if os.path.exists("topic_specific.csv"):
            topic_relevancy = pd.read_csv("topic_specific.csv", index_col=[0])
            for each in topics:
                topic_relevancy.loc[each["item_text"], msg] = int(topic_relevancy.loc[each["item_text"], msg]) + 1
                topic_based_relevance[each["item_text"]][msg] = int(topic_relevancy.loc[each["item_text"], msg])
                topic_based_relevance[each["item_text"]][relevant_irrelevant_map[msg]] = int(topic_relevancy.loc[each["item_text"]][relevant_irrelevant_map[msg]])
                topic_relevancy["Relevant"].astype(str)
                topic_relevancy["Irrelevant"].astype(str)
            topic_relevancy.to_csv("topic_specific.csv")
            for each in topic_based_relevance:
                topic_based_relevance[each]["Relevant"] = str(topic_relevancy["Relevant"][each])
                topic_based_relevance[each]["Irrelevant"] = str(topic_relevancy["Irrelevant"][each])
        else:
            frame = pd.DataFrame(columns = ["Relevant", "Irrelevant"], index=["Politics", "HealthCare", "Technology", "Education", "Environment"])
            for each in topics:
                frame.loc[each["item_text"]][msg] = 1
                frame.loc[each["item_text"]][relevant_irrelevant_map[msg]] = 0
                topic_based_relevance[each["item_text"]][msg] = frame.loc[each["item_text"]][msg]
            frame.to_csv("topic_specific.csv")
        print(topic_based_relevance)
        return jsonify(msg = topic_based_relevance)
    else:
        return jsonify(msg = topic_based_relevance)

@app.route("/close", methods=["POST"])
def close_chat():
    print("Close the File.")
    if os.path.exists("topic_specific.csv"):
        os.remove("topic_specific.csv")
    else:
        print("The file does not exist")
    
    return jsonify(msg="ok")



if __name__ == "__main__":
    app.run(debug=True)