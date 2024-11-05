import time
from time import sleep
from tqdm import tqdm

def main():
    a_list = range(1000)
    ret = 0
    for elem in ft_progress(a_list):
        ret += (elem + 3) % 5
        sleep(0.01)
    print()
    print(ret)


def ft_progress(lst: int) -> int:
    # Captura o tempo inicial antes do loop 
    start_time = time.time()
    
    # Inicializa o tqdm 
    t = tqdm(lst, bar_format="{l_bar}{bar}|{n_fmt}/{total_fmt} elapsed time: {elapsed}s",)
    
    for i in t:
        # Captura o tempo atual
        current_time = time.time()

        # Calcula o tempo decorrido desde o início do loop até agora
        elapsed_time = current_time - start_time

        # Calcula o tempo médio por iteração
        avg_time_per_iteration = elapsed_time / (i + 1)

        # Calcula o número restante de iterações
        remaining_iterations = len(lst) - (i + 1)

        # Estima o tempo restante
        eta = avg_time_per_iteration * remaining_iterations
        
        # Formata o eta com duas casas decimais
        formatted_eta = f"{eta:.2f}s"
        
        # Seta a descrição do tqdm 
        t.set_description(f"ETA {formatted_eta}")

        # Retorna o valor i para chamada
        yield i

if __name__ == "__main__":
    main()