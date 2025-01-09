from flask import Flask, request, jsonify
import mysql.connector
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
import json

app = Flask(__name__)

db = mysql.connector.connect(
    host = "remark-db.cus0iutxtxoy.ap-south-1.rds.amazonaws.com",
    database = "remarkhr",
    user = "remarkawsdb",
    password = "nHDL]&<P9Oj-~lKvre5d#rUSJKH?",
    port = 3306
)


google_api_key = 'AIzaSyDUz3IyqiQJyIGIJpvVm4eui2lAPRlvSF8'
llm = ChatGoogleGenerativeAI(model='gemini-1.5-pro-latest', temperature=0.7, google_api_key=google_api_key)
conversation_chain = ConversationChain(llm=llm)


def generate_keys(profile):

    key_prompt = f"""

    Generate a list of important keywords and skills that are closely associated with the job title '{profile}'.
    These should include relevent Core skills(suggest all possible skills),Languages(all maximum possible languages used in production),Frameworks(all frameworks used in production),Databases(all Database used in production) and tools(all tools used in production).
    For each category (Skills, Languages, Frameworks, Databases, and Tools), provide only specific and relevant examples without any additional descriptions or explanations. 
    Only mention tools, databases, or frameworks that are directly used in production, without general or non-relevant statements.
    Responce must be msot relevent and specfic according to the given job title.
    Provide data in key value formet while maintaining the formation and sequence.
    Do provide newest technologies as well.
    Make sure the genrated keys must have 10 values.
    """
    
    response = conversation_chain.run(input=key_prompt)
    start_index = response.find('{')
    end_index = response.rfind('}')
    response_json_str = response[start_index:end_index+1]
    response_json = json.loads(response_json_str)
    return response_json

@app.route('/generate_keys', methods=['POST'])
def generate_profile_keys():
    if request.method == 'POST':
        # profile = request.form['profile']
        data = request.get_json()

        if not data or 'profile' not in data:
            return jsonify({'error': 'No profile provided'}), 400

        profile = data['profile']

    
        keywords = generate_keys(profile)
        
    
        cursor = db.cursor()
        cursor.execute("SELECT `des_key` FROM designation WHERE des_name = %s", (profile,))
        result = cursor.fetchone()

        if result:
            
            existing_keywords = json.loads(result[0])
            return jsonify({'profile': profile, 'keywords': existing_keywords})

        sql = "INSERT INTO designation (des_name, `des_key`) VALUES (%s, %s)"
        val = (profile,json.dumps(keywords))
        cursor.execute(sql, val)
        db.commit()

        
        return jsonify({'profile': profile, 'keywords': keywords})

if __name__ == "__main__":
    app.run(debug=True)