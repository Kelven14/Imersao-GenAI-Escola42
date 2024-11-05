import sys
import requests
from bs4 import BeautifulSoup


def main(): 

    if len(sys.argv) != 2:
        print("Não foi inserido a palavra corretamente. Padrão: python request_wikipedia.py <palavra>")
        return
        
    search = sys.argv[1]
    
    title, content = find_text_wikipedia(search)
        
    if title:
        text_clean = extract_text(content)
        filename = title.replace(' ', '_').lower()
        write_file(filename, text_clean)
        print(f"Dados sobre '{filename}' foi salvo com sucesso no arquivo '{filename}.wiki' ")
    

def find_text_wikipedia(search):

    # Parâmetros para a chamada da API Wikipedia - Procurar artigos 
    params_article = { 
        "action"  :"query",
        "list"    :"search",
        "prop"    :"info",
        "inprop"  :"url",
        "utf8"    : "",
        "format"  :"json",
        "srlimit" :"1",
        "srsearch":search
    }

    # Response da API Wikipedia para procurar os artigos 
    response_articles = request_api_wikipedia(params_article)
    
    # Obtem o titulo do artigo encontrado
    title_article = extract_first_title(response_articles)

    if title_article: 
        # Parâmetros para a chamada da API
        params = {
            "action": "query",
            "format": "json",
            "titles": title_article,
            "prop": "extracts"
        }

        # Response da API Wikipedia para procurar a palavra procurada 
        response_search = request_api_wikipedia(params)

        #Obtem o texto da primeira página encontrada
        content = extract_first_page(response_search)
        
        return title_article, content
    else: 
        print("Não foi encontrado nenhuma página")
        return None, None


# Função genérica para fazer uma requisição na API do Wikipedia 
def request_api_wikipedia(params):
    
    # Linguagem 
    language = 'pt'

    # URL base da API da Wikipedia
    url = f"https://{language}.wikipedia.org/w/api.php"
    
    response = requests.get(url, params = params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception ("Error ao requisitar a API: {response.status_code}") 


# Extrair o titulo do primeiro artigo
def extract_first_title(response_json):
    try:
        if len(response_json['query']['search']) >0:
            first_result = response_json['query']['search'][0]
            return first_result['title']
        else: 
            return None
    except (KeyError, IndexError, TypeError) as e:
        raise Exception (f"Erro ao extrair o titulo: {e}")

# Função para obter o 'extract'
def extract_first_page(response_json):
    try:
        first_page_id = next(iter(response_json['query']['pages']))
        first_page = response_json['query']['pages'][first_page_id]
        return first_page['extract']
    except (KeyError, IndexError, TypeError) as e:
        raise Exception (f"Erro ao extrair o texto: {e}")

# Função para escrever o arquivo 
def write_file (filename, content):
    try:
        with  open(filename + ".wiki", 'w') as file : 
            file.write(content)
            file.close()
    except IOError:
        raise Exception ("Erro: Não foi possível escrever no arquivo.")
    except Exception as e:
        raise Exception (f"Erro inesperado: {e}")


# Função para converte o texto extraido do Wikipedia
def extract_text(texto_html):
    try:
        soup = BeautifulSoup(texto_html, 'html.parser')
        return soup.get_text()
    except Exception as e:
        raise Exception (f"Erro ao analisar o HTML: {e}")

if __name__ == "__main__":
    main()