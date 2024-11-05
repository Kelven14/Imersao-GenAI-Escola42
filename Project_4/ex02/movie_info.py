import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re
import time

# Carrega as variáveis de ambiente
load_dotenv("./config.env")

movie_titles = ["The Matrix", "Inception", "Pulp Fiction", "The Shawshank Redemption", "The Godfather"]


# Função para formatar o prompt
def format_prompt(movie_title):
    return f'''
    Forneça informações detalhadas sobre o filme "{movie_title}" em formato JSON. 
    Certifique-se de incluir o título, ano, diretor, gêneros, resumo da trama e quaisquer curiosidades relevantes. 
    Comece sua resposta com:
    {{
    "title": "{movie_title}",
    '''


def clean_response(response):
    response = re.sub(r'\s+', ' ', response)  # Remove espaços em excesso
    return response.strip()  # Remove espaços no início e no final


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
            "max_output_tokens": 500,
            "response_mime_type": "text/plain",
        }
    )

    try:
        response = model.start_chat().send_message(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro durante a chamada à API: {str(e)}")
        return None


def get_movie_info(title):
    prompt = format_prompt(title)
    return call_gemini(prompt)


# Função principal
def main():
    for title in movie_titles:
        print(f"\nAnalisando: {title}")
        result = get_movie_info(title)
        if result:
            cleaned_result = clean_response(result)

            if len(cleaned_result) < 50:
                print("Erro: Resposta muito curta para ser um JSON válido.")
                continue

            try:
                movie_info = json.loads(cleaned_result)

                # Acessando o gênero
                genre = movie_info.get('genre') or movie_info.get('genres', [])

                print(f"title: {movie_info['title']}")
                print(f"year: {movie_info['year']}")
                print(f"director: {movie_info['director']}")
                print(f"genre: {genre}")
                print(f"plot_summary: {movie_info.get('plot_summary', movie_info.get('plot', 'N/A'))}")
            except json.JSONDecodeError:
                print("Erro: Falha ao gerar um JSON válido")
                print(f"Resposta recebida foi:\n{cleaned_result}")
            except KeyError as e:
                print(f"Chave esperada ausente na resposta JSON: {e}")
            except Exception as e:
                print(f"Erro inesperado: {str(e)}")
        else:
            print("Erro: Nenhuma resposta recebida do modelo.")

        # Pausa para evitar limites da API
        time.sleep(1)
        print("-" * 50)


if __name__ == "__main__":
    main()
