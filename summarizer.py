try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
import torch
import os

class SlideSummarizer:
    def __init__(self, model_code:int = 0):
        """
        Inicializa o modelo de Deep Learning.
        """
        
        self.model_name = self.get_model_name(model_code)

        if self.model_name.split("/")[0] == "API":
            return
        else:
            print(f"--- Carregando modelo de IA: {self.model_name} ---")
            
            print(f"-> Rodando em GPU (se disponível)")

            # Detecta se CUDA está disponível e ajusta o device
            if torch.cuda.is_available():
                self.device = 0  # GPU
            else:
                self.device = -1  # CPU
            
            if TRANSFORMERS_AVAILABLE:
                try:
                    self.summarizer = pipeline("summarization", model=self.model_name, device=self.device)
                except Exception as e:
                    print(f"[ERRO FATAL] Falha ao carregar modelo: {e}")
                    self.summarizer = None
            else:
                print("[ERRO] Biblioteca 'transformers' não instalada.")
                self.summarizer = None

    def get_model_name(self, model_code: int) -> str:
        match model_code:
            case 0:
                return "facebook/bart-large-cnn" #ok
            case 1:
                return "sshleifer/distilbart-cnn-12-6" #ok
            case 2:
                return "rhaymison/t5-portuguese-small-summarization" #razoável
            # case 3:
            #     return "csebuetnlp/mT5_m2m_crossSum_enhanced " #não funcionou
            case 3:
                return "API/gemini-2.0-flash-lite"
            # case 4:
            #     return "google/pegasus-cnn_dailymail" #não funcionou
            case 4:
                return "API/gemini-2.5-flash-lite"
            case 5:
                return "philschmid/bart-large-cnn-samsum" #zoadasso, textos em inglês e outras coisas desconhecidas
            case _:
                return "facebook/bart-large-cnn" #default

    def gerar_topicos(self, texto_longo, chave_api=None, max_length: int =130, min_length: int =30):
        if chave_api:
            if not GEMINI_AVAILABLE:
                print("[ERRO] Biblioteca 'google-generativeai' não instalada. Use 'pip install google-generativeai'.")
                return ["ERRO: API do Gemini não disponível."]
            return self.gerar_topicos_remote(texto_longo, chave_api, max_length, min_length)
        else:
            return self.gerar_topicos_local(texto_longo, max_length, min_length)
    
    def gerar_topicos_local(self, texto_longo, max_length=130, min_length=30):
        """
        Recebe um texto longo e retorna uma lista de frases (bullet points).
        """
        if not self.summarizer:
            return ["ERRO: IA não disponível."]

        # O texto já vem limpo do Ingestor (ASCII), não precisamos limpar de novo.
        n_palavras = len(texto_longo.split())

        # Se for muito curto, não resume
        if n_palavras < 40:
            return [texto_longo]

        # Ajuste dinâmico de tamanho
        input_len_estimado = int(n_palavras * 1.3)
        dynamic_max = min(max_length, int(input_len_estimado * 0.8))
        dynamic_min = min(min_length, int(dynamic_max * 0.5))
        
        if dynamic_max < 20: dynamic_max = 20
        if dynamic_min < 10: dynamic_min = 10

        try:
            # Tenta gerar o resumo
            # truncation=True é essencial
            resumo_raw = self.summarizer(
                texto_longo, 
                max_length=dynamic_max, 
                min_length=dynamic_min, 
                do_sample=False, 
                truncation=True
            )
            texto_resumido = resumo_raw[0]['summary_text']
            
        except Exception as e:
            print(f"   [AVISO] Erro na IA. Usando fallback. Detalhe: {e}") 
            return texto_longo.split('. ')[:3]

        # Pós-processamento
        frases = texto_resumido.split('. ')
        topicos = []
        for frase in frases:
            f = frase.strip()
            if f and len(f) > 5:
                if not f.endswith('.'):
                    f += '.'
                topicos.append(f)
                
        return topicos
    
    def gerar_topicos_remote(self, texto_longo, chave_api, max_length=100, min_length=30):
        """
        Usa a API do Gemini para gerar os bullet points.
        """
        print("--- Usando API Remota (Gemini) ---")
        if not chave_api:
            return ["ERRO: Chave de API do Gemini não fornecida."]

        try:
            genai.configure(api_key=chave_api)
            model = genai.GenerativeModel(self.model_name.split('/')[1])
        except Exception as e:
            return [f"ERRO: Falha ao configurar a API do Gemini. Detalhe: {e}"]

        prompt = f"""
        Você é um especialista em criar apresentações de slides. Sua tarefa é resumir o texto a seguir em, no máximo, 5 bullet points concisos e informativos.
        O texto é um trecho de um artigo acadêmico ou documento técnico. Extraia apenas as informações mais cruciais.
        Cada bullet point deve ser uma frase completa e terminar com um ponto.
        Limite o total de tokens do resumo a no máximo {max_length} tokens.

        Texto para resumir:
        ---
        {texto_longo}
        ---

        Resumo em bullet points:
        """

        try:
            response = model.generate_content(prompt)
            texto_resumido = response.text.strip()
            
            # O Gemini pode retornar o texto com marcadores como '*' ou '-'. 
            # Vamos limpar e separar em frases.
            frases = texto_resumido.replace('*', '').replace('-', '').split('\n')
            topicos = []
            for frase in frases:
                f = frase.strip()
                if f and len(f) > 10: # Filtra linhas vazias ou curtas
                    if not f.endswith('.'):
                        f += '.'
                    topicos.append(f)
            if not topicos:
                 return ["Não foi possível gerar um resumo com a API."]

            return topicos

        except Exception as e:
            print(f"   [AVISO] Erro na API do Gemini. Detalhe: {e}") 
            return ["ERRO: Falha ao chamar a API do Gemini."]
