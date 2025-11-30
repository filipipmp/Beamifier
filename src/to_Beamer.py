import os
import re  # Adicionado para manipulação avançada de strings

class BeamerBuilder:
    def __init__(self):
        # TODO: adicionar escolha de tema
        # Reintroduzimos o adjustbox para redimensionar TABELAS (tabular) especificamente
        self.base_preambulo = r"""
            \documentclass{beamer}
            \usepackage[utf8]{inputenc}
            \usepackage[T1]{fontenc}
            \usepackage{graphicx}
            \usepackage{booktabs}
            \usepackage{multirow}
            \usepackage{tikz}
            \usetikzlibrary{arrows.meta, positioning, shapes.geometric}
            \usepackage[utf8]{inputenc}
            
            \usepackage{amsmath}
            \usepackage{graphicx,url}
            \usepackage{adjustbox}  % Essencial para forçar a tabela a caber na tela
            \usetheme{Madrid}
            
            % Configuração para numeração de legendas
            \setbeamertemplate{caption}[numbered]
            
            % Remove os ícones de navegação padrão do Beamer que poluem a tela
            \setbeamertemplate{navigation symbols}{}
            
            % Metadados dinâmicos aqui
            \title{{{TITULO}}}
            \author{{{AUTOR}}}
            \date{\today}
            
            \begin{document}
            
            \frame{\titlepage}
        """
        self.fim = r"\end{document}"

    def _limpar_codigo_asset(self, codigo):
        """
        Limpa incompatibilidades e força redimensionamento.
        """
        # 1. Remove asteriscos (figure* -> figure)
        codigo = codigo.replace('figure*', 'figure')
        codigo = codigo.replace('table*', 'table')
        
        # 2. REMOVE PARÂMETROS DE POSICIONAMENTO [htbp], [h], [t!]
        # Regex: Procura \begin{table} seguido opcionalmente de [...]
        # Substitui apenas pelo \begin{table} limpo
        codigo = re.sub(r'\\begin\{(figure|table)\}(\[.*?\])?', r'\\begin{\1}', codigo)

        # 3. Força redimensionamento inteligente de tabelas
        # Envolve o ambiente 'tabular' em um 'adjustbox'
        if 'tabular' in codigo and 'adjustbox' not in codigo:
            # Substitui o início do tabular
            codigo = re.sub(
                r'(\\begin\{tabular.*?\})', 
                r'\\begin{adjustbox}{max width=\\textwidth, max height=0.75\\textheight}\n\1', 
                codigo
            )
            # Substitui o fim do tabular
            codigo = codigo.replace(r'\end{tabular}', r'\end{tabular}' + '\n' + r'\end{adjustbox}')
        
        # 4. Garante centralização
        if r'\centering' not in codigo:
            codigo = codigo.replace(r'\begin{figure}', "\\begin{figure}\\centering")
            codigo = codigo.replace(r'\begin{table}', "\\begin{table}\\centering")
            
        return codigo

    def criar_slides_secao(self, titulo, topicos, assets):
        """
        Gera um ou mais frames para uma única seção.
        """
        slides_code = ""
        safe_titulo = titulo.replace('&', r'\&').replace('%', r'\%')

        # --- FRAME 1: O Resumo (Texto) ---
        if topicos: 
            slides_code += f"\\begin{{frame}}\n"
            slides_code += f"  \\frametitle{{{safe_titulo}}}\n"
            slides_code += f"  \\begin{{itemize}}\n"
            
            for item in topicos:
                safe_item = item.replace('&', r'\&').replace('%', r'\%').replace('$', r'\$')
                slides_code += f"    \\item {safe_item}\n"
                
            slides_code += f"  \\end{{itemize}}\n"
            slides_code += f"\\end{{frame}}\n\n"

        # --- FRAMES EXTRAS: Tabelas e Figuras ---
        for i, asset in enumerate(assets):
            codigo_asset = self._limpar_codigo_asset(asset['codigo'])
            tipo_label = "Figura" if asset['tipo'] == 'figura' else "Tabela"
            
            # Mantemos o [shrink] como segurança extra, mas o trabalho pesado
            # agora é feito pelo adjustbox dentro do _limpar_codigo_asset
            slides_code += f"\\begin{{frame}}[shrink]\n" 
            slides_code += f"  \\frametitle{{{safe_titulo} - {tipo_label} {i+1}}}\n"
            slides_code += f"  \\vspace{{0.2cm}}\n"
            
            slides_code += codigo_asset + "\n"
            
            slides_code += f"\\end{{frame}}\n\n"
            
        return slides_code

    def montar_apresentacao_completa(self, lista_slides, output_path="output.tex", metadados=None):
        if metadados is None:
            metadados = {"titulo": "Apresentação", "autor": ""}
            
        conteudo_total = self.base_preambulo.replace("{{TITULO}}", metadados['titulo'])
        conteudo_total = conteudo_total.replace("{{AUTOR}}", metadados['autor'])
        
        for slide_data in lista_slides:
            assets = slide_data.get('assets', [])
            conteudo_total += self.criar_slides_secao(
                slide_data['titulo'], 
                slide_data['conteudo'], 
                assets
            )
            
        conteudo_total += self.fim
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(conteudo_total)
            
        return os.path.abspath(output_path)

if __name__=='__main__':
    pass