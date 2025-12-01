# Beamifier
This small project was carried out for the Deep Learning (Aprendizado
Profundo) course integrating Unesp's Post-Graduate Program in Computer Science (Programa de Pós-Graduação em Ciência da Computação (PPGCC) da Unesp): https://www.ibilce.unesp.br/#!/pos-graduacao/programas-de-pos-graduacao/ciencia-da-computacao/apresentacao/

 This course was taught by Professor Denis Henrique Pinheiro Salvadeo during the second semester of 2025.

## Installation

The project was developed using Python 3.12.3 and the libraries (and versions) specified in requirements.txt in Ubuntu 24.04.3 / WSL

Clone this github repository and install the requirements with

    pip install -r requirements.txt

Your google api key can be either provided to the respective summarizer class when initialized, to the pipeline when initialized or using the environmental variable API_KEY

    export API_KEY="YOUR_API_KEY"

## Usage
    from src.pipeline import Beamifier_Pipeline 
    
    pipeline = Beamifier_Pipeline(model=model, api_key=api_key, _compile=True, remove_trash=True)

    pipeline.run(input_path, output_path)

- <strong>model</strong> can either be the summarizer model's identifier (string) or its initialized class (check summarizers_dict inside summarizer.py for implemented models and identifiers)
- <strong>api_key</strong> can either be your api key (string) or set to None (if an api is used and api_key is set to None, it will attempt do gather it from the local variable API_KEY).
- <strong>_compile</strong> determines whether or not the pipeline attempts to compile the generated Beamer's .tex using pdfLaTeX
- <strong>remove_trash</strong> determines whether or not the pipeline deletes auxiliary files generated during the .tex file compilation if _compile is set to True

## License

Distributed under the MIT License. See LICENSE for more information.

Project Link: https://github.com/filipipmp/Beamifier