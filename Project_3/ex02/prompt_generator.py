import os
import google.generativeai as genai
from dotenv import load_dotenv

def main():
    load_dotenv("./config.env")
    
    exemplos = ler_exemplo('examples.txt')
    for exemplo in exemplos:
        prompt = format_prompt(
            exemplo['role'],
            exemplo['task'],
            exemplo['topic'],
            exemplo['specificQuestion']
        )
        response = query_gemini(prompt)
        print (response)

def query_gemini(prompt):
    # Configure your API key from the environment variable
    api_key_genai = os.getenv('GEMINI_API_KEY')
    
    if api_key_genai is None:
        raise ValueError("API key Gemini not found. Please set the GEMINI_API_KEY environment variable.")

    genai.configure(api_key=api_key_genai)
  
    try:
        print("############################## NOVA CONSULTA ########################################")
        print("Consultando Gemini...")
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }
        )
        
        response = model.start_chat().send_message(prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def format_prompt(role, task, topic, specific_question):
    # Formatando o prompt
    prompt = f"""
        Atue como descrito na tag <role>.
        As respostas devem ser em português.
        Seu objetivo é <task> sobre o tópico <topic>. A partir desse contexto, responda a pergunta do campo <specific_question> de forma clara e acessível, incluindo exemplos práticos quando apropriado.
        
        A resposta final deve seguir a seguinte ordem em negrito:
        
        **### 1. Explicação básica do conceito:**
        **### 2. Analogia do cotidiano:**
        **### 3. Solução passo a passo da pergunta:**
        **### 4. Exemplo detalhado seguido por lista em itens de exemplos simples:**
        **### 5. Dica prática para iniciantes:**
        
        <role>
        {role}
        </role>

        <task>
        {task}
        </task>
        
        <topic>
        {topic}
        </topic>
        
        <specific_question>
        {specific_question}
        </specific_question>
    """
    return prompt

# Função para ler e separar os dados do arquivo
def ler_exemplo(arquivo):
    with open(arquivo, 'r') as file:
        conteudo = file.read()

    grupos = conteudo.strip().split("\n\n")
    exemplos = []

    for grupo in grupos:
        linhas = grupo.split("\n")
        role = linhas[0].split("= ")[1].strip('\"')
        task = linhas[1].split("= ")[1].strip('\"')
        topic = linhas[2].split("= ")[1].strip('\"')
        specific_question = linhas[3].split("= ")[1].strip('\"')

        exemplos.append({
            'role': role,
            'task': task,
            'topic': topic,
            'specificQuestion': specific_question
        })

    return exemplos

if __name__ == "__main__":
    main()
