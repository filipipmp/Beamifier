from transformers import pipeline, AutoTokenizer
import google.generativeai as genai

import torch
import os



#==============================================================================================================
# GENERAL CLASSES FOR SUMMARIZERS
# GENERAL CLASS FOR GOOGLE API MODEL
class Google_API_Model:
    def __init__(self, model_name, api_key=None):
        # Basic info
        self.model_name = model_name
        if api_key is None:
            api_key = os.environ[f'{model_name}_API_KEY']
        self.api_key = api_key
        # Gets model
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def summarize(self, text, max_length=130, min_length=30, prompt=None):
        # Standard prompt (if not defined)
        if prompt is None:
            prompt = f"""
                Você é um especialista em criar apresentações de slides. Sua tarefa é resumir o texto a seguir em, no máximo, 5 bullet points concisos e informativos.
                O texto é um trecho de um artigo acadêmico ou documento técnico. Extraia apenas as informações mais cruciais.
                Cada bullet point deve ser uma frase completa e terminar com um ponto.
                Limite o total de tokens do resumo a no máximo {max_length} tokens.

                Texto para resumir:
                ---
                {text}
                ---

                Resumo em bullet points:
            """
        # Gets response
        response = self.model.generate_content(prompt)
        raw_text = response.text.strip()
        # Cleaning markers gemini can return, like '*' or '-'.
        sentences = raw_text.replace('*', '').replace('-', '').split('\n')
        topics = []
        for sentence in sentences:
            f = sentence.strip()
            if f and len(f) > 10: # Filters small or empty lines
                if not f.endswith('.'):
                    f += '.'
                topics.append(f)
        if not topics:
             return ["Não foi possível gerar um resumo com a API."]
        return topics

# GENERAL CLASS FOR TRANSFORMERS MODEL
class Transformers_Model:
    def __init__(self, model_name, device=None):
        self.model_name = model_name
        # Basic info
        if device is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.device = device
        # Gets model
        self.summarizer = pipeline("summarization", model=self.model_name, device=self.device, truncation=True)
    
    def summarize(self, text, max_length=130, min_length=30):
        # Doesn't summarize if text is already small
        n_words = len(text.split())
        if n_words < 40:
            return [text]

        # Dynamic length
        estimated_input_len = int(n_words * 1.3)
        dynamic_max = min(max_length, int(estimated_input_len * 0.8))
        dynamic_min = min(min_length, int(dynamic_max * 0.5))
        
        if dynamic_max < 20: dynamic_max = 20
        if dynamic_min < 10: dynamic_min = 10

        summary_raw = self.summarizer(
            text, 
            max_length=dynamic_max, 
            min_length=dynamic_min, 
            do_sample=False, 
            truncation=True,
        )
        summary = summary_raw[0]['summary_text']

        # Post processing
        sentences = summary.split('. ')
        topics = []
        for sentence in sentences:
            f = sentence.strip()
            if f and len(f) > 5:
                if not f.endswith('.'):
                    f += '.'
                topics.append(f)                
        return topics
#==============================================================================================================



#==============================================================================================================
# CUSTOM CLASSES FOR SUMMARIZERS
# facebook/bart-large-cnn
class bart_large_cnn_summarizer(Transformers_Model):
    def __init__(self, device=None, api_key=None):
        super().__init__(model_name="facebook/bart-large-cnn", device=device)
    def summarize(self, text, max_length=130, min_length=30):
        # Doesn't summarize if text is already small
        n_words = len(text.split())
        if n_words < 40:
            return [text]

        # Dynamic length
        estimated_input_len = int(n_words * 1.3)
        dynamic_max = min(max_length, int(estimated_input_len * 0.8))
        dynamic_min = min(min_length, int(dynamic_max * 0.5))
        
        if dynamic_max < 20: dynamic_max = 20
        if dynamic_min < 10: dynamic_min = 10

        # Method not inherited soleny because of this line
        self.summarizer.tokenizer.model_max_length = dynamic_max
        summary_raw = self.summarizer(
            text, 
            max_length=dynamic_max, 
            min_length=dynamic_min, 
            do_sample=False, 
            truncation=True,
        )
        summary = summary_raw[0]['summary_text']

        # Post processing
        sentences = summary.split('. ')
        topics = []
        for sentence in sentences:
            f = sentence.strip()
            if f and len(f) > 5:
                if not f.endswith('.'):
                    f += '.'
                topics.append(f)                
        return topics

# sshleifer/distilbart-cnn-12-6
class destilbart_cnn_summarizer(Transformers_Model):
    def __init__(self, device=None, api_key=None):
        super().__init__(model_name="sshleifer/distilbart-cnn-12-6", device=device)

# rhaymison/t5-portuguese-small-summarization
class t5_portuguese_small_summarizer(Transformers_Model):
    def __init__(self, device=None, api_key=None):
        super().__init__(model_name="rhaymison/t5-portuguese-small-summarization", device=device)

# API/gemini-2.0-flash-lite
class gemini_2_0_flash_lite(Google_API_Model):
    def __init__(self, api_key=None, device=None):
        super().__init__(model_name="gemini-2.0-flash-lite", api_key=api_key)

# API/gemini-2.5-flash-lite
class gemini_2_5_flash_lite(Google_API_Model):
    def __init__(self, api_key=None, device=None):
        super().__init__(model_name="gemini-2.5-flash-lite", api_key=api_key)

# API/gemma-3-27b-it
class gemma_3_27b_it(Google_API_Model):
    def __init__(self, api_key=None, device=None):
        super().__init__(model_name="gemma-3-27b-it", api_key=api_key)
    def summarize(self, text, max_length=130, min_length=30, prompt=None):
        topics = super().summarize(text, max_length, min_length, prompt)
        fs = topics[0].lower()
        if fs.startswith("aqui est") or fs.startswith("here`s") or fs.startswith("here’s") or fs.startswith("here's") or fs.startswith("here is"):
            topics.pop(0)
        return topics

# API/gemma-3-12b-it
class gemma_3_12b_it(Google_API_Model):
    def __init__(self, api_key=None, device=None):
        super().__init__(model_name="gemma-3-12b-it", api_key=api_key)
    def summarize(self, text, max_length=130, min_length=30, prompt=None):
        topics = super().summarize(text, max_length, min_length, prompt)
        fs = topics[0].lower()
        if fs.startswith("aqui est") or fs.startswith("here`s") or fs.startswith("here’s") or fs.startswith("here's") or fs.startswith("here is"):
            topics.pop(0)
        return topics
#==============================================================================================================



summarizers_dict = {
    'bart':                  bart_large_cnn_summarizer,
    'destilbart':            destilbart_cnn_summarizer,
    't5_portuguese_small':   t5_portuguese_small_summarizer,
    'gemini_2.0_flash_lite': gemini_2_0_flash_lite,
    'gemini_2.5_flash_lite': gemini_2_5_flash_lite,
    'gemma-3-27b-it':        gemma_3_27b_it,
    'gemma-3-12b-it':        gemma_3_12b_it
}



if __name__=='__main__':
    pass