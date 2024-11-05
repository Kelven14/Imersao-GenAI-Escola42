import sys
import requests
from bs4 import BeautifulSoup

def main():
    if len(sys.argv) != 2:
        print("Não foi inserido o titulo corretamente. Padrão: python roads_to_philosophy.py <titulo>")
        return
    
    search_term = sys.argv[1]
    visited_links = set()
    
    current_title = search_term
    total_visited = 0

     # Exibe a primeira visita
    print(f"Visitando: {current_title}")

    while True:
        # print(f"Buscando: {current_title}")
        
        response = request_wikipedia(current_title)
        if response is None:
            break
        
        visited_links.add(current_title)
        total_visited += 1
        
        if current_title.lower() == 'philosophy':
            print(f"{total_visited} roads from {search_term} to philosophy!")
            break
        
        next_link = find_next_link(response)
        
        if next_link is None:
            print("It leads to a dead end!")
            break
        
        if next_link in visited_links:
            print("It leads to an infinite loop!")
            break
        
        current_title = next_link

def request_wikipedia(search_term):
    url = f"https://en.wikipedia.org/wiki/{search_term}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response
        elif response.status_code in [301, 302]:  # Redirecionamentos
            redirected_url = response.url
            return requests.get(redirected_url)
        else:
            print(f"Error: {response.status_code} - Unable to continue.")
            return None
    except requests.RequestException as e:
        print(f"Error: {e}. Unable to continue.")
        return None

def find_next_link(response):
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontra todos os parágrafos da página
        paragraphs = soup.find_all('p')
        
        for paragraph in paragraphs:
            for link in paragraph.find_all('a'):
                if link.get_text() and not is_ignored_link(link):
                    title = link['href'].split('/')[-1]  # Extrai o título da Wikipedia
                    print(f"Visitando: {title}")
                    return title

        return None
    except Exception as e:
        print(f"Error: {e}. Unable to continue.")
        return None


def is_ignored_link(link):
    # Ignora links que estão em itálico, entre parênteses ou que não levam a novos artigos
    if link.find_parent('i') or link.find_parent('em'):
        return True
    if link.get_text().startswith('(') or link.get_text().endswith(')'):
        return True
    return False

if __name__ == "__main__":
    main()
