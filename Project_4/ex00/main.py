import os
import git
import json
import shutil
import logging
import requests
import google.generativeai as genai

from datetime import datetime
from github import Github
from dotenv import load_dotenv


# Carregar variáveis de ambiente do arquivo .env
load_dotenv("./config.env")
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CodeAnalyzer:
    def __init__(self, github_token):
        self.github_token = github_token
        self.logger = logging.getLogger(__name__)

    def analyze_code(self, file_content):
        prompt = self.create_prompt(file_content)
        try:
            self.logger.info("Consultando Gemini...")
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 50,
                    "max_output_tokens": 1000,
                    "response_mime_type": "application/json",
                }
            )
            response = model.start_chat().send_message(prompt)

            # Acessando o conteúdo da resposta corretamente
            suggestions = response.text.strip()
            print("Conteúdo da resposta:", suggestions)  # Print para depuração

            # Adiciona colchetes para formatar como um array JSON
            suggestions = f"[{suggestions}]"

            try:
                suggestions_json = json.loads(suggestions)
                if isinstance(suggestions_json, list):
                    return suggestions_json
                else:
                    self.logger.error("A resposta não é uma lista JSON.")
                    return []
            except json.JSONDecodeError:
                self.logger.error("A resposta não é um JSON válido. Conteúdo da resposta: %s", suggestions)
                return []
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Erro HTTP: {e.response.status_code} - {e.response.text}")
            return []
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao conectar à API do Gemini: {e}")
            return []
        except ValueError as e:
            self.logger.error(f"Erro ao processar a resposta da API: {e}")
            return []

    def create_prompt(self, file_content):
        prompt = f"""
            você é o melhor agente para análise de códigos de funções para arquitetura serverless em linguagem python.
            Você é o especialista em realizar as análises de obsolescência: uma revisão de código que busca todas 
            'breaking changes' de uma base de códigos serverless em python e a necessidade de correção de versões de dependências de bibliotecas
            e ou códigos, funções, classes e ou módulos depreciados em novas versões da linguagem.

            Aqui há um resumo das etapas que você deve realizar durante a análise, bem como as suas premissas: 
            - A versão do python a ser utilizada como base para análise será sempre a versão do Python 3.12
            - Você analisa o código em python de funções serverless em busca de modificações necessárias e que ocasionariam erros ao serem 
            executadas nas versões mais novas de python(breaking changes), tais como: 
                1) Sintaxes 'depreciadas'
                2) Versões de bibliotecas e dependências que necessitam de atualizações
                3) Qualquer trecho no código considerado obsoleto para ser executado na versão de python utilizada para análise.

            Após a análise, realize a revisão de todo conteúdo gerado, se certificando que todas as premissas descritas foram cumpridas. Alguns pontos importantes na revisão:
            - Certifique-se que o resumo apresentado esteja dentro das premissas e do escopo
            - Certifique-se que o resumo está feito na formatação correta.
            - Verifique toda sugestão de código e certifique que esteja aderente com o item proposto e sua descrição detalhada
            - Cheque se a linguagem está compatível com a premissa proposta
            - Certifique-se que os itens propostos estejam ligados apenas à obsolescência e 'breaking changes'

            Identifique os trechos de código que estão obsoletos ou não compatíveis com a versão do python 3.12. Retornar apenas as 2 primeiras obsolescência encontrada, retorne um objeto JSON com a seguinte estrutura: 

            {{
            "line_number": "numero da linha",
            "current_code": "codigo atual",
            "suggested_fix": "correção sugerida",
            "reason": "razao da sintaxe"
            }}

            A saída final deve ser em formato JSON, contendo todas as linhas onde as mudanças são necessárias e as respectivas sugestões.

            Realize a análise de obsolescência do <codigo>{file_content}</codigo>
        """
        return prompt

    def validate_suggestions(self, suggestions):
        try:
            suggestions_json = json.loads(suggestions)
            if not isinstance(suggestions_json, list):
                raise ValueError("Sugestões devem ser uma lista.")

            for suggestion in suggestions_json:
                if not all(key in suggestion for key in ["line_number", "current_code", "suggested_fix", "reason"]):
                    raise ValueError("Sugestões recebidas não têm a estrutura correta.")
        except json.JSONDecodeError:
            raise ValueError("A resposta não é um JSON válido.")


class GitHubManager:
    def __init__(self, repo_url, token):
        self.repo_url = repo_url
        self.token = token
        self.repo_name = "/".join(repo_url.split("/")[-2:]).replace('.git', '')

        # Gerar sufixo de data e hora
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d-%H%M%S')
        self.local_repo_path = os.path.join(os.getcwd(), f"{self.repo_name}-{timestamp}")

        self.github = Github(self.token)
        self.logger = logging.getLogger(__name__)

    def clone_repository(self):
        if os.path.exists(self.local_repo_path):
            shutil.rmtree(self.local_repo_path)
        self.logger.info(f"Clonando o repositório {self.repo_name}...")

        try:
            git.Repo.clone_from(self.repo_url, self.local_repo_path)
        except git.exc.GitCommandError as e:
            self.logger.error(f"Erro ao clonar o repositório: {e}")
            raise

    def create_pull_request(self, branch_name, all_suggestions):
        """Cria um pull request no GitHub com comentários sobre obsolescências."""

        # Verificar se o repositório existe
        try:
            repo = self.github.get_repo(self.repo_name)
        except Exception as e:
            self.logger.error(f"Erro ao acessar o repositório: {e}")
            return

        # Criar a branch
        try:
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=repo.get_branch("main").commit.sha)
        except Exception as e:
            self.logger.warning(f"Falha ao criar branch '{branch_name}': {e}")

        # Adicionar comentários como alterações
        comments = []
        for file_name, suggestions in all_suggestions.items():
            for suggestion in suggestions:
                line_number = suggestion['line_number']
                reason = suggestion['reason']
                current_code = suggestion['current_code']
                suggested_fix = suggestion['suggested_fix']
                comment = (
                    f"### {file_name} (Linha {line_number})\n"
                    f"- **Obsolescência detectada:** {reason}\n"
                    f"- **Codigo atual:** {current_code}\n"
                    f"- **Sugestão:** {suggested_fix}\n\n"
                )
                comments.append(comment)

        # Criar um novo arquivo com os comentários
        comments_file_path = "obsolescence_comments.md"
        with open(comments_file_path, 'w', encoding='utf-8') as comments_file:
            comments_file.write("# Comentários sobre Obsolescências\n\n")
            comments_file.write("\n".join(comments))

        # Usar gitpython para adicionar e commitar
        try:
            local_repo = git.Repo(self.local_repo_path)  # Usar o caminho correto
            # Verifica se a branch já existe localmente
            if branch_name not in local_repo.git.branch().split():
                local_repo.git.checkout('main')  # Volta para a branch main
                local_repo.git.checkout('-b', branch_name)  # Cria e troca para a nova branch

            local_repo.git.add(comments_file_path)  # Adiciona o arquivo
            local_repo.git.commit(message="Adicionando comentários sobre obsolescências.")  # Comita as alterações
            local_repo.git.push("origin", branch_name)  # Faz push das alterações para a nova branch
        except Exception as e:
            self.logger.error(f"Erro ao adicionar e commitar: {e}")
            raise

        # Criar o pull request
        pr_body = "Este PR contém comentários sobre obsolescências identificadas:\n\n" + "\n".join(comments)
        repo.create_pull(title="Comentários sobre obsolescência", body=pr_body, head=branch_name, base="main")
        self.logger.info("Pull request criado com sucesso.")


def main(github_url):
    analyzer = CodeAnalyzer(GITHUB_TOKEN)
    git_manager = GitHubManager(github_url, GITHUB_TOKEN)

    git_manager.clone_repository()

    os.chdir(git_manager.local_repo_path)  # Mude para o diretório do repositório clonado

    all_suggestions = {}

    for root, _, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                with open(file_path, 'r') as f:
                    file_content = f.read()

                suggestions = analyzer.analyze_code(file_content)
                all_suggestions[file] = suggestions

    # Gerar nome de branch com data e hora
    now = datetime.now()
    branch_name = f"comments-obsolescence-{now.strftime('%Y%m%d-%H%M%S')}"
    git_manager.create_pull_request(branch_name, all_suggestions)


if __name__ == "__main__":
    github_url = input("Insira a URL do projeto no GitHub: ")
    main(github_url)
