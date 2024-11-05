import os
import google.generativeai as genai
from dotenv import load_dotenv
import json


def main():
    # Load environment variables
    load_dotenv("./config.env")

    github_comments = load_github_comments("./github_commets.json")

    if github_comments is None or len(github_comments) == 0:
        print("Nenhum comentário encontrado para analisar.")
        return

    analyze_sentiments(github_comments)

    # Print results
    for comment in github_comments:
        print(f"Texto: {comment['text']}")
        print(f"Sentimento: {comment['sentiment']}")
        print("-" * 50)


def load_github_comments(file_path):
    """Load GitHub comments from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar o JSON: {e}")
        return None  # Retorna None se houver erro
    except FileNotFoundError:
        print("Arquivo github_comments.json não encontrado.")
        return None  # Retorna None se o arquivo não for encontrado


def call_llm(text):
    """Call the LLM API to analyze sentiment."""
    # Configure your API key from the environment variable
    api_key_genai = os.getenv('GEMINI_API_KEY')

    if api_key_genai is None:
        raise ValueError("API key Gemini not found. Please set the GENAI_API_KEY environment variable.")

    genai.configure(api_key=api_key_genai)

    # Create the prompt with examples
    prompt = format_prompt(text)

    try:
        print("Consultando Gemini...")
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 50,
                "max_output_tokens": 64,
                "response_mime_type": "text/plain",
            }
        )

        response = model.start_chat().send_message(prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def format_prompt(comment_text):
    """Format the prompt for LLM analysis."""
    prompt = f"""
        Sua tarefa é analisar o seguinte feedback e classificar o sentimento. Use os exemplos abaixo como guia:

        <exemplos>
            <exemplo>
                <texto>A implementação está ótima!</texto>
                <sentimento>Positivo</sentimento>
            </exemplo>

            <exemplo>
                <texto>O código precisa de melhorias.</texto>
                <sentimento>Negativo</sentimento>
            </exemplo>

            <exemplo>
                <texto>A documentação está razoável, mas pode ser melhor.</texto>
                <sentimento>Neutro</sentimento>
            </exemplo>
        </exemplos>

        Agora, analise o seguinte feedback:
        <texto>{comment_text}</texto>
        <sentimento> 
    """
    return prompt


def parse_llm_response(response):
    """Parse the LLM response to determine sentiment."""
    if response:
        # Normaliza a resposta
        response = response.strip().lower()

        # Verifica o sentimento na resposta
        if "positivo" in response:
            return "Positivo"
        elif "negativo" in response:
            return "Negativo"
        elif "neutro" in response:
            return "Neutro"
        else:
            return "Desconhecido"
    return "Desconhecido"


def analyze_sentiments(comments):
    """Analyze sentiments of the provided comments."""
    for comment in comments:
        llm_response = call_llm(comment["text"])
        comment["sentiment"] = parse_llm_response(llm_response)


if __name__ == "__main__":
    main()
