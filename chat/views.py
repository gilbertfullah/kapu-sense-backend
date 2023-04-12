from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import Message

from langchain import ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.vectorstores import Pinecone
import pinecone 
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import os
from langchain.prompts.chat import (ChatPromptTemplate, SystemMessagePromptTemplate, AIMessagePromptTemplate, HumanMessagePromptTemplate,)
from langchain.schema import (AIMessage, HumanMessage, SystemMessage)
from langchain.document_loaders import DirectoryLoader
from langchain.chains import VectorDBQA
from TTS.api import TTS
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.utilities import SerpAPIWrapper
import whisper
from dotenv import load_dotenv

load_dotenv()


class MessageView(APIView):
    def post(self, request):
        message = request.data.get('message')
        
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
        PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
        
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        os.environ["SERPAPI_API_KEY"] = SERPAPI_API_KEY

        # initialize pinecone
        pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")

        index_name = "election"
        chat = ChatOpenAI(temperature=0, model='gpt-3.5-turbo')

        loader = DirectoryLoader("MyDrive/AI", glob="**/*.txt")
        documents = loader.load()

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(documents)

        embeddings = OpenAIEmbeddings()
        docsearch = Pinecone.from_documents(docs, embeddings, index_name=index_name)

        system_template = """Use the following pieces of context to answer the users questions. If you don't know, just say that you don't know, 
                            don't try to make up an answer.
                            --------------------
                            {context}"""

        messages = [
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template("{question}")
        ]
        prompt = ChatPromptTemplate.from_messages(messages)

        chain_type_kwargs = {"prompt": prompt}
        qa = VectorDBQA.from_chain_type(llm=chat, chain_type="stuff", vectorstore=docsearch, chain_type_kwargs=chain_type_kwargs)  

        search = SerpAPIWrapper()
        tools = [
            Tool (
                name = "election_qa",
                func=qa.run,
                description="Use the following pieces of context to answer the users questions. Use this more unless it does not know the answer then use Search to answer the question.",
                ),
            
            Tool(
                name = "Search", 
                func = search.run, 
                description = "useful only when the answer is not on the context from the database"
                )
        ]

        agent = initialize_agent(tools, chat, agent="zero-shot-react-description", verbose=True) 
        
        reply = agent.run(message)
        
        response_data = {
            'message': reply,
            'isMe': True,
        }
        
        message = Message.objects.create(question=message, response=reply)

        return Response(response_data, status=status.HTTP_200_OK)
