from src.extractor import LatexIngestor
from src.summarizer import SlideSummarizer
from src.to_Beamer import BeamerBuilder

import subprocess



#==============================================================================================================
# CUSTOM CLASSES FOR RUNNING THE PIPELINE
class Beamifier_Pipeline():
    # TODO: deixar compile aqui ou no run?
    def __init__(self, model_code=0, api_key=None, _compile=False, remove_trash=True):
        self.model_code = model_code
        self.compile = _compile
        self.remove_trash = remove_trash

        self.api_key = api_key
        self.summarizer = SlideSummarizer(model_code)
        
    def run(self, input_path, output_path=None):
        if output_path is None:
            output_path = input_path[:-4]+"_beamer.tex"
        
        # Parser
        print("=== 1. Lendo e Parseando LaTeX ===")
        ingestor = LatexIngestor()
        texto_full = ingestor.carregar_projeto_recursivo(input_path)

        secoes = ingestor.extrair_secoes(texto_full)
        metadados = ingestor.extrair_metadados(texto_full)

        print(f"-> Título: {metadados['titulo']}")
        print(f"-> Seções: {len(secoes)}")

        # Resumos
        print("\n=== 2. Inicializando Engine de IA ===")
        

        slides_prontos = []
        print("\n=== 3. Gerando Resumos ===")
        for i, secao in enumerate(secoes):
            print(f"Processando [{i+1}/{len(secoes)}]: {secao['titulo']}...")
            bullet_points = self.summarizer.gerar_topicos(secao['conteudo'], self.api_key)
            slides_prontos.append({
                "titulo": secao['titulo'],
                "conteudo": bullet_points,
                "assets": secao.get("assets", [])
            })

        # Geracao de beamer
        print("\n=== 4. Montando Beamer final ===")
        builder = BeamerBuilder()

        caminho_final = builder.montar_apresentacao_completa(
            slides_prontos, 
            output_path, 
            metadados=metadados
        )

        print(f"\n[SUCESSO] Arquivo .tex gerado em: {caminho_final}")

        if self.compile:
            print("\n=== 5. Compilando PDF Beamer ===")
            #comando = ["pdflatex", "-interaction=nonstopmode", 
            #            f'-output-directory={"/".join(output_path.split("/")[:-1])}',
            #            f'{caminho_final}']
            comando = ["pdflatex", "-interaction=batchmode", 
                        f'-output-directory={"/".join(output_path.split("/")[:-1])}',
                        f'{caminho_final}']
            subprocess.run(comando)
            if self.remove_trash:
                for extension in ["aux", "log", "nav", "out", "snm", "toc"]:
                    comando = ["rm", f'{output_path[:-4]+"."+extension}']
                    subprocess.run(comando)
#==============================================================================================================