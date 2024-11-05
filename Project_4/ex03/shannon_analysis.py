import os
import google.generativeai as genai
from dotenv import load_dotenv
import re

# Carrega as variáveis de ambiente
load_dotenv("./config.env")


def extract_content(text, tag):
    import re
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""


def call_gemini(prompt):
    api_key_genai = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=api_key_genai)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "max_output_tokens": 500,
            "response_mime_type": "text/plain",
        }
    )

    response = model.start_chat().send_message(prompt)
    return response.text.strip()


def run_prompt_chain():
    # Etapa 1: Obter uma visão geral da vida e carreira de Claude Shannon
    prompt1 = '''
    Forneça uma visão geral da vida e carreira de Claude Shannon, o pai da teoria da informação. 
    Estruture sua resposta usando a tag <vida_carreira>.
    '''
    response1 = call_gemini(prompt1)
    vida_carreira = extract_content(response1, "vida_carreira")
    print(vida_carreira)

    # Etapa 2: Analisar suas principais contribuições para a teoria da informação
    prompt2 = f'''
    Com base na visão geral fornecida, analise as principais contribuições de Claude Shannon para a teoria da informação. 
    Use as informações da etapa anterior: <vida_carreira>{vida_carreira}</vida_carreira>.
    Estruture sua resposta usando a tag <contribuicoes>.
    '''
    response2 = call_gemini(prompt2)
    contribuicoes = extract_content(response2, "contribuicoes")
    print(contribuicoes)

    # Etapa 3: Explorar o impacto de seu trabalho na computação moderna e nas tecnologias de comunicação
    prompt3 = f'''
    Com base nas contribuições mencionadas e na visão geral da vida e carreira de Claude Shannon, explore o impacto do trabalho de Claude Shannon na computação moderna e nas tecnologias de comunicação. 
    Use as informações das etapas anteriores: 
    <vida_carreira>{vida_carreira}</vida_carreira> 
    <contribuicoes>{contribuicoes}</contribuicoes>.
    Estruture sua resposta usando a tag <impacto>.
    '''
    response3 = call_gemini(prompt3)

    impacto = extract_content(response3, "impacto")
    print(impacto)

    # Etapa 4: Sintetizar as informações das etapas anteriores em uma análise abrangente
    prompt4 = f'''
    Com base nas informações a seguir, sintetize uma análise abrangente sobre Claude Shannon:
    
    <vida_carreira>{vida_carreira}</vida_carreira>
    <contribuicoes>{contribuicoes}</contribuicoes>
    <impacto>{impacto}</impacto>
    
    Resuma essas informações e estruture sua resposta usando a tag <analise_final>.
    '''
    response4 = call_gemini(prompt4)
    analise_final = extract_content(response4, "analise_final")

    # Exibe a análise final
    print(analise_final)


if __name__ == "__main__":
    run_prompt_chain()
