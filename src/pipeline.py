from src.extractor import LatexIngestor
from src.summarizer import summarizers_dict
from src.to_Beamer import BeamerBuilder

import subprocess



#==============================================================================================================
# CUSTOM CLASSES FOR RUNNING THE PIPELINE
class Beamifier_Pipeline():
    def __init__(self, model, device=None, api_key=None, _compile=False, remove_trash=True):
        if isinstance(model,str):
            model = summarizers_dict[model]
        self.summarizer = model(device=device, api_key=api_key)
        self.compile = _compile
        self.remove_trash = remove_trash
        
    def run(self, input_path, output_path=None):
        if output_path is None:
            output_path = input_path[:-4]+"_beamer.tex"
        
        # Parser
        print("=== 1. Lendo e Parseando LaTeX ===")
        extractor = LatexIngestor()
        full_text = extractor.carregar_projeto_recursivo(input_path)

        sections = extractor.extrair_secoes(full_text)
        metadata = extractor.extrair_metadados(full_text)

        print(f"-> Título: {metadata['titulo']}")
        print(f"-> Seções: {len(sections)}")

        # Resumos
        print("\n=== 2. Inicializando Engine de IA ===")
        

        slides = []
        print("\n=== 3. Gerando Resumos ===")
        for i, section in enumerate(sections):
            print(f"Processando [{i+1}/{len(sections)}]: {section['titulo']}...")
            bullet_points = self.summarizer.summarize(section['conteudo'])
            slides.append({
                "titulo": section['titulo'],
                "conteudo": bullet_points,
                "assets": section.get("assets", [])
            })

        # Geracao de beamer
        print("\n=== 4. Montando Beamer final ===")
        builder = BeamerBuilder()

        final_path = builder.montar_apresentacao_completa(
            slides, 
            output_path, 
            metadados=metadata
        )

        print(f"\n[SUCESSO] Arquivo .tex gerado em: {final_path}")

        if self.compile:
            print("\n=== 5. Compilando PDF Beamer ===")
            command = ["pdflatex", "-interaction=batchmode", 
                        f'-output-directory={"/".join(output_path.split("/")[:-1])}',
                        f'{final_path}']
            subprocess.run(command)
            if self.remove_trash:
                for extension in ["aux", "log", "nav", "out", "snm", "toc"]:
                    command = ["rm", f'{output_path[:-4]+"."+extension}']
                    subprocess.run(command)
#==============================================================================================================