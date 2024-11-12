import psycopg2
import json
import re
import pinecone
import time
import os
import random
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt
from PyPDF2 import PdfReader
from pinecone import Pinecone, ServerlessSpec, PodSpec


load_dotenv()
client = OpenAI()
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)
embed_model = "text-embedding-3-small"
index_name = 'mediwise-kb'
delimiter = "####"
limit = 8000  #set the limit of knowledge base words, leave some space for chat history and query.

GPT_MODEL = "gpt-4o"
def chat_complete_messages(messages, temperature):
    completion = client.chat.completions.create(
        model=GPT_MODEL,
        messages= messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
    return completion.choices[0].message.content


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, temperature=0, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


def get_postgres_conn():
    connection_string = "dbname='medapp' user='postgres' host='0.0.0.0' password='password' port='5432'"
    try:
        conn = psycopg2.connect(connection_string)
        conn.autocommit = True
    except:
        print("I am unable to connect to the database")
    return conn


def get_appointments(medical_record_number):
    conn = get_postgres_conn() # get postgres conn
    with conn:
        with conn.cursor() as curs:
            try:
                curs.execute("SELECT row_to_json(appointments) FROM appointments where patient_medical_record_number=%s", [medical_record_number])
                appointment_rows = curs.fetchall()
                # print(f"{appointment_rows}")
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
    
    out = {}
    if len(appointment_rows) != 0:
        for app in appointment_rows[0]:          
            out['doctor_name'] = app['doctor_name']
            out['appointment_time'] = app['appointment_start_ts']
    return json.dumps(out)

def get_existing_patient_medical_record_numbers():
    conn = get_postgres_conn() # get postgres conn
    with conn:
        with conn.cursor() as curs:
            try:
                curs.execute("SELECT row_to_json(patients) FROM patients")
                patient_rows = curs.fetchall()
                # print(f"{appointment_rows}")
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
    
    mrn_ret = []
    out = {}
    print(patient_rows)
    if len(patient_rows) != 0:
        for app in patient_rows:        
            out[app[0]['medical_record_number']] = True
            mrn_ret.append(out)
    print(mrn_ret)
    return json.dumps(mrn_ret)

def generate_patient_medical_record_numbers(first_name, last_name):
    name = first_name + last_name
    new_mrn = 'MRN' + str(random.randint(10,99)) + ''.join([random.choice(name) for i in range(4)])
    out = {}   
    out['generated_medical_record_number'] = new_mrn
    return json.dumps(out)

def table_dml(dml):
    conn = get_postgres_conn()
    error_code = 0
    result = None
    with conn:
        with conn.cursor() as curs:
            try:
                print(dml)
                # Assuming you have an active connection and cursor
                curs.execute(dml)

                # Only fetch results for SELECT queries
                if dml.strip().lower().startswith('select'):
                    result = curs.fetchall()
                    out = {}
                    if len(result) == 0:
                        result = {"return": "No information returned by the query"}
                        return result
                    else:
                        if len(result) != 0:
                            for app in result[0]:
                                print(app)       
                                out['result'] = app
                                return json.dumps(out)
                else:
                    result = None

            except (Exception, psycopg2.Error) as e:
                print("Error while executing DML in PostgreSQL", e)
                error_code = 1
    if error_code != 1 and result == None:
        result = json.dumps({'Changes': 'Successful'})
        return result
    else:
        final_res = {"code": error_code, "res": result}
        print(final_res)
        return final_res


# A list of functions with descriptions for the LLM to use
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_appointments",
            "description": "Get the current patient appointment details",
            "parameters": {
                "type": "object",
                "properties": {
                    "medical_record_number": {
                        "type": "string",
                        "description": "The medical_record_number",
                    },
                },
                "required": ["medical_record_number"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "table_dml",
            "description": "Select update insert or delete into appointments or patients table by SQL",
            "parameters": {
                "type": "object",
                "properties": {
                    "dml": {
                        "type": "string",
                        "description": f"""SQL statement to do select update insert and delete on a table, 
                        the SQL should be written using the following database schema:
                        Table name: appointments
                        ####Columns Names and type: 
                            appointment_id SERIAL PRIMARY KEY,
                            doctor_name VARCHAR(50) NOT NULL,
                            patient_medical_record_number  VARCHAR(50) NOT NULL,
                            appointment_start_ts timestamp NOT NULL,
                            created_ts timestamp NOT NULL                       
                      ####  
                      Table name: patients
                      #### column name and type:
                            patient_id SERIAL PRIMARY KEY,
                            patient_name VARCHAR(50) NOT NULL,
                            date_of_birth DATE NOT NULL,
                            medical_record_number VARCHAR(50) NOT NULL,
                            symptoms VARCHAR(50) NULL,
                            doctor_type_requested  VARCHAR(50) NULL,
                            chat_summary TEXT,
                            consent BOOLEAN DEFAULT False
                        ####
                        when creating a new appointment record:
                            a) make sure to populate medical record number column with 'MRN' in the given medical record number string and current local timestamp for the created_ts column
                               in the appointments table  
                            b) Also check if the patient already has an appointment with the same doctor before 
                               creating a new appointment
                            c) If an appointment exists for the patient with the same doctor then update the appointment start ts and created ts columns  
                        When checking for patient consent in the patients table
                            a) check for the value contained in the column consent in the patients table.
                            b) if the consent column for the patient is True then the patient has already given the consent.
                        when inserting a new patient record into patients table
                            a) use the generated medical record number, given patient date of birth and concatenate first name and last name to make patient name.
                            b) If the patient medical record number already exists then update the row instead of inserting
                        """,
                    },
                    
                },
                "required": ["dml"],
            }
        }
    }, 
    {
        "type": "function",
        "function": {
            "name": "generate_patient_medical_record_numbers",
            "description": "Generate new patient medical record number",
            "parameters": {
                "type": "object",
                "properties": {
                    "first_name": {
                        "type": "string",
                        "description": "patients first name",
                    },
                    "last_name": {
                        "type": "string",
                        "description": "patients last name",
                    },
                },
                "required": ["first_name", "last_name"],
            },
        }
    },
]

available_functions = {
            "get_appointments": get_appointments,
            "table_dml": table_dml,
            "generate_patient_medical_record_numbers": generate_patient_medical_record_numbers,
        }

def tool_call(messages, response_message, tool_calls):

    messages.append(response_message)  # extend conversation with assistant's reply

    if tool_calls:

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = "you should not be seeing this" # To prevent it from accessing the variable before initialization

            if function_name == 'get_appointments':
                function_response = function_to_call(
                    medical_record_number=function_args.get("medical_record_number"),
                    )
            elif function_name == 'table_dml':
                function_response = function_to_call(
                    dml=function_args.get("dml"),
                )
            elif function_name == 'generate_patient_medical_record_numbers':
                function_response = function_to_call(
                    first_name=function_args.get("first_name"),
                    last_name=function_args.get("last_name"),
                )
            print(function_response)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
            
            second_response = chat_completion_request(messages, temperature=0, tools=tools, tool_choice="auto")
            print(f"second_response: {second_response}")
            bot_response = second_response.choices[0].message.content

    return bot_response

def index_exists(index_name):
    # Retrieve the list of indexes and store in a variable
    indexes_info = pc.list_indexes()
    
    # Access the 'indexes' key which contains the list of index dictionaries
    for index in indexes_info:
        # Check if the 'name' key in each index dictionary matches the index_name
        if index['name'] == index_name:
            return True
    return False

def create_index(index_name):
    if not index_exists(index_name):
        print(f"Index {index_name} does not exist.")

        pc.create_index(
            name= index_name,
            dimension=1536,
            metric="cosine",
            spec=PodSpec(
                environment="gcp-starter"
                )
            )
        index = pc.Index(index_name)
        # view index stats
        # print(index.describe_index_stats())

def split_text_into_lines(input_text, max_words_per_line):
    words = input_text.split()
    lines = []
    current_line = []

    for word in words:
        if len(current_line) + len(word) + 1 <= max_words_per_line:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))
    return lines


#process the knowledge base file upsert to a namespace
#from tqdm import tqdm

def nlp_upsert(filename, index_name, name_space, nlp_id, chunk_size, stride, page_begin, page_end):
    """
    upsert a whole PDF file (with begin page and end page information) to the pinecone vector database

    Parameters:
    filename (str): The file name.
    index_name (str): The pinecone index name.
    name_space (str): The namespace we want to place for all related docuement.
    nlp_id (str): A common ID prefix to reference to document. 
    chunk_size (int): The chunk size, how many lines as one chunks. 
    stride (int): The overlap side, how many lines as overlap between chunks. 
    page_begin (int): Which page in the PDF file to begin for upsert.
    page_end (int): Which page is the ending page for upsert. 

    Returns:
    None: No return.
    """
    doc = ""
    
    reader = PdfReader(filename)  
    
    for i in range(page_begin, page_end):
        doc += reader.pages[i].extract_text() 
        # print("page completed:", i)    
      

    doc = split_text_into_lines(doc, 30)
    # print("The total lines: ", len(doc))

    
    #Connect to index
    index = pc.Index(index_name)
    
    count = 0
    for i in range(0, len(doc), chunk_size):
        #find begining and end of the chunk
        i_begin = max(0, i-stride)
        i_end = min(len(doc), i_begin+chunk_size)
        
        doc_chunk = doc[i_begin:i_end]
        # print("-"*80)
        # print("The ", i//chunk_size + 1, " doc chunk text:", doc_chunk)
        
        
        texts = ""
        for x in doc_chunk:
            texts += x
        # print("Texts:", texts)
        
        #Create embeddings of the chunk texts
        try:
            res = client.embeddings.create(input=texts, model=embed_model)
        except:
            done = False
            while not done:
                time.sleep(10)
                try:
                    res = client.embeddings.create(input=texts, model=embed_model)
                    done = True
                except:
                    pass
        embed = res.data[0].embedding
        # print("Embeds length:", len(embed))

        # Meta data preparation
        metadata = {
            "text": texts
        }

        count += 1
        # print("Upserted vector count is: ", count)
        # print("="*80)

        #upsert to pinecone and corresponding namespace

        index.upsert(vectors=[{"id": nlp_id + '_' + str(count), "metadata": metadata, "values": embed}], namespace=name_space)


files = ['/data/Chatbot Corpus PDF.pdf']
def build_kb(index_name):
    create_index(index_name)
    print(os.getcwd())
    path = os.getcwd()

    for f in files:
        filename = path+f
        print("Knowledge base file name:", filename)
        reader = PdfReader(filename)  
        page_len = len(reader.pages)

        # print("length of the knowledge base file:", page_len)
        nlp_upsert(filename, index_name, "mediwisekb","nlp", 5, 2, 0, page_len)
        index = pc.Index(index_name)
        print(index.describe_index_stats())
    state = 'Reusing KnowledgeBase'
    return state


def get_input_embedding(input):
    # print("input:", input)
    res = client.embeddings.create(
    input=[input],
    model=embed_model
    )
    return res

def retrive_from_pinecone(res, index):
    # retrieve from Pinecone
    xq = res.data[0].embedding

    # get relevant contexts
    res = index.query(vector=xq,
                    top_k=3,
                    include_metadata=True,
                    namespace='mediwisekb')
    contexts = [
        x["metadata"]["text"] for x in res["matches"]
    ]
    return contexts

def build_prompt(contexts):
    prompt = " "
    
    # append contexts until hitting limit
    count = 0
    proceed = True
    while proceed and count < len(contexts):
        if len(prompt) + len(contexts[count]) >= limit:
            proceed = False 
        else:
            prompt += contexts[count]
        
        count += 1
    # End of while loop
    
    prompt = delimiter + prompt + delimiter
    
    return prompt

def build_context_query_knowledge(input, prompt, chatContext):
    input = input + " "
    input_message = {"role": "user", "content": f"""
                    {input}
                    """
                    }
    knowledge_message = {"role": "system", "content": f"""
                        {prompt}
                        """    
                        }
    context_query_knowledge = chatContext + [knowledge_message, input_message]
    # print("context_query_knowledge: ", context_query_knowledge)
    return context_query_knowledge