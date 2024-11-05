import os
import ollama
from groq import Groq
import google.generativeai as genai
from dotenv import load_dotenv


def main():

    load_dotenv("./config.env")

    with open("./job_description.txt", "r") as file:
        job_description = file.read()
    formatted_prompt = format_prompt(job_description)
    results = query_all_models(formatted_prompt)
    for model, response in results.items():
        print(f"\nAnálise do {model}:")
        print(response)
        print("-" * 50)


def query_gemini(prompt):
    
    # Configure your API key from the environment variable
    api_key_genai = os.getenv('GEMINI_API_KEY')
    
    if api_key_genai is None:
        raise ValueError("API key Gemini not found. Please set the GENAI_API_KEY environment variable.")

    genai.configure(api_key=api_key_genai)
  
    try:
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

def query_llama(prompt):
    try:
        print("Consultando Ollama...")
        response = ollama.chat(model='qwen2:1.5b', messages=[{'role': 'user','content': prompt}])
        return response['message']['content']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def query_groq(prompt):
    
    try:
        client_groq = Groq()
        completion = client_groq.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        print("Consultando Groq...")
        return completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def format_prompt(job_description):
    
    # Formatando o prompt
    prompt = f"""
        Você possui o cargo de especialista na área de recursos humanos.
        Preencha os '*Campos para preencher:*' baseado na 'descrição de vaga' a seguir.
        
        *Descrição de vaga:*
        {job_description}
        -------------
        *Campos para preencher:* 
        Name of role: 
        Working hours: 
        Country: 
        Tech skills:
    """

    return prompt


def query_all_models(prompt):
    models = ["Gemini", "Ollama", "groq"]
    results = {model: query_model(model, prompt) for model in models}
    return results

def query_model(model_name, prompt):
    if model_name == "Gemini":
        return query_gemini(prompt)
    elif model_name == "groq":
        return query_groq(prompt)
    elif model_name == "Ollama":
        return query_llama(prompt)
    else:
        return "Modelo não reconhecido."


if __name__ == "__main__":
    main()