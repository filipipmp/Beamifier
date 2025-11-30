import os
import re


#==============================================================================================================
# CUSTOM CLASSES FOR EXTRACTING USEFUL TEXT FROM .tex
# Baseado em expressoes regulares
class LatexIngestor:
    def __init__(self):
        self.secoes = []

    def _ler_arquivo_seguro(self, caminho_arquivo):
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return f.read()

    def carregar_projeto_recursivo(self, caminho_arquivo):
        def substituir_input(match):
            nome_sub_arquivo = match.group(1)
            if not nome_sub_arquivo.endswith('.tex'):
                nome_sub_arquivo += '.tex'
            caminho_completo = os.path.join(diretorio_base, nome_sub_arquivo)
            return self.carregar_projeto_recursivo(caminho_completo)
        
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        # Regex para inputs
        pattern_input = r'\\(?:input|include)\{([^}]+)\}'
        return re.sub(pattern_input, substituir_input, conteudo)

    def pre_processar_texto(self, latex_source):
        # Remove comentários
        clean_text = re.sub(r'(?<!\\)%.*', '', latex_source)
        # Normaliza espaços
        return re.sub(r'\s+', ' ', clean_text).strip()

    def _limpar_comando_latex(self, texto):
        #Remove comandos comuns do LaTeX como \textbf{}, \IEEEauthorblockN{}, etc.
        #deixando apenas o texto interno.
        if not texto: return ""
        
        # 1. Substitui comandos conhecidos do IEEE e formatação simples
        # Ex: \IEEEauthorblockN{Nome} -> Nome
        texto = re.sub(r'\\IEEEauthorblock[NA]\{', '', texto)
        texto = re.sub(r'\\textbf\{', '', texto)
        texto = re.sub(r'\\textit\{', '', texto)
        texto = re.sub(r'\\emph\{', '', texto)

        # 2. Converte comandos de separação
        texto = re.sub(r'\\and', ', ', texto)
        texto = re.sub(r'\\', ' ', texto) # Remove quebras de linha manuais

        # 3. Limpeza final de caracteres residuais (chaves que sobraram)
        texto = texto.replace('{', '').replace('}', '')
        
        # 4. Normaliza espaços
        return re.sub(r'\s+', ' ', texto).strip()

    def _extrair_e_remover_assets(self, texto_secao):
        """
        Identifica ambientes de Figura e Tabela, extrai o código LaTeX bruto
        e remove do texto principal (para não confundir a IA de resumo).
        """
        assets = []

        # Regex para capturar Figuras (incluindo figure*)
        # O .*? é non-greedy (pega o mínimo possível até o end)
        pattern_fig = r'(\\begin\{figure\*?\}.*?\\end\{figure\*?\})'
        figs = re.findall(pattern_fig, texto_secao, re.DOTALL)
        assets.extend([{'tipo': 'figura', 'codigo': f} for f in figs])
        
        # Remove as figuras do texto
        texto_limpo = re.sub(pattern_fig, '', texto_secao, flags=re.DOTALL)

        # Regex para capturar Tabelas (incluindo table*)
        pattern_tab = r'(\\begin\{table\*?\}.*?\\end\{table\*?\})'
        tabs = re.findall(pattern_tab, texto_limpo, re.DOTALL)
        assets.extend([{'tipo': 'tabela', 'codigo': t} for t in tabs])

        # Remove as tabelas do texto
        texto_limpo = re.sub(pattern_tab, '', texto_limpo, flags=re.DOTALL)

        return texto_limpo, assets

    def extrair_metadados(self, latex_completo):
        """
        Busca \title{} e \author{} no texto completo com limpeza aprimorada.
        """
        texto_limpo = self.pre_processar_texto(latex_completo)
        metadados = {
            "titulo": "Apresentação sem Título",
            "autor": "Autor Desconhecido"
        }

        # Busca Título
        match_title = re.search(r'\\title\{([^}]*)\}', texto_limpo, re.IGNORECASE | re.DOTALL)
        if match_title:
            metadados["titulo"] = self._limpar_comando_latex(match_title.group(1))

        # Busca Autor
        match_author = re.search(r'\\author\{([^}]*)\}', texto_limpo, re.IGNORECASE | re.DOTALL)
        if match_author:
            metadados["autor"] = self._limpar_comando_latex(match_author.group(1))

        return metadados

    def extrair_secoes(self, latex_completo):
        texto_limpo = self.pre_processar_texto(latex_completo)
        
        match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', texto_limpo, re.DOTALL)
        if not match: return []
        corpo = match.group(1)
        
        partes = re.split(r'\\section\{([^}]*)\}', corpo)
        resultado = []
        
        # TODO: deixamos assim?
        # Processa contexto (abstract/intro)
        if len(partes[0].strip()) > 50:
            texto_conteudo, assets = self._extrair_e_remover_assets(partes[0].strip())
            resultado.append({
                "titulo": "Contexto", 
                "conteudo": texto_conteudo,
                "assets": assets
            })

        # Processa seções numeradas
        for i in range(1, len(partes), 2):
            titulo = partes[i].strip()
            raw_conteudo = partes[i+1].strip()
            
            # Separa o texto narrativo dos objetos visuais
            texto_conteudo, assets = self._extrair_e_remover_assets(raw_conteudo)
            
            if "biblio" not in titulo.lower() and "reference" not in titulo.lower():
                resultado.append({
                    "titulo": titulo, 
                    "conteudo": texto_conteudo,
                    "assets": assets # Nova chave contendo a lista de tabelas/imagens
                })
                
        return resultado
#==============================================================================================================



if __name__=='__main__':
    ingestor = LatexIngestor()
    texto_full = ingestor.carregar_projeto_recursivo("example/marcos.tex")

    secoes = ingestor.extrair_secoes(texto_full)
    metadados = ingestor.extrair_metadados(texto_full)

    # Debbg
    with open("example/extractor-metadados.txt",'w') as f:
        for key, value in metadados.items():
            f.write(f'{key}: {value}\n')
    with open("example/extractor-secoes.txt",'w') as f:
        for i, secao in enumerate(secoes):
            f.write(f'SECAO-{i}:\ntitulo:{secao['titulo']}\nconteudo:{secao['conteudo']}\nassets:{secao['assets']}\n')
