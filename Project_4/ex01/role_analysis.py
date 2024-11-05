import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv("./config.env")

# Define os papéis
roles = {
    "Educador tradicional": "Você é um educador tradicional com anos de experiência em universidades convencionais. Analise a École 42 de uma perspectiva acadêmica.",
    "Estudante de tecnologia": "Você é um estudante de tecnologia ansioso para aprender programação. Analise a École 42 do ponto de vista de um potencial aluno.",
    "Recrutador de tecnologia": "Você é um recrutador de profissionais de uma grande empresa de tecnologia. Avalie a École 42 considerando as habilidades que você busca em candidatos."
}

# Prompt do usuário
user_prompt = "Descreva a École 42 e seu método de ensino. Destaque os pontos principais que seriam relevantes para sua perspectiva."


# Função para formatar o prompt
def format_prompt(role_description, user_prompt):
    """Format the prompt for LLM analysis."""
    prompt = f"""
        {role_description}

        Com base na sua experiência e perspectiva, por favor, responda à seguinte pergunta:

        {user_prompt}
    """
    return prompt


# Função para chamar o modelo Gemini
def call_gemini(prompt):
    api_key_genai = os.getenv('GEMINI_API_KEY')
    genai.configure(api_key=api_key_genai)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "max_output_tokens": 150,
            "response_mime_type": "text/plain",
        }
    )

    response = model.start_chat().send_message(prompt)
    return response.text.strip()  # Remove espaços em branco extras


# Função para chamar o modelo Llama
def call_llama(prompt):
    # Simulação de chamada ao modelo Llama
    return f"Simulação de resposta do modelo Llama para: {prompt.strip()}"


# Função para gerar respostas com base nos papéis
def generate_responses(user_prompt):
    responses = {}
    for role, system_prompt in roles.items():
        full_prompt = format_prompt(system_prompt, user_prompt)

        gemini_response = call_gemini(full_prompt)
        # llama_response = call_llama(full_prompt)

        responses[role] = {
            "Gemini": gemini_response
            # "Llama": llama_response
        }

    return responses


# Função principal
def main():
    print("=== Análises usando GEMINI ===")
    responses = generate_responses(user_prompt)

    for role, response in responses.items():
        print(f"--- Análise da perspectiva de {role} ---")
        print(f"Gemini: {response['Gemini']}")
        # print(f"Llama: {response['Llama']}")
        print("-" * 50)


if __name__ == "__main__":
    main()
