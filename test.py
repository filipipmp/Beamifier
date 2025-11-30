from src.pipeline import Beamifier_Pipeline

import os
import timeit

if __name__=='__main__':
    model_dict = {
        0:"bart",
        1:"destbart",
        2:"t5-pt",
        3:"gemini-2.0-flash-lite",
        4:"gemini-2.5-flash-lite",
    }
    pessoas = [
        "marcos",
        "guilherme"
    ]
    api_key = os.environ['API_KEY']

    for code, modelname in model_dict.items():
        pipeline = Beamifier_Pipeline(model_code=code, api_key=api_key, _compile=True, remove_trash=True)
        for pessoa in pessoas:
            input_path  = f'example/{pessoa}/main.tex'
            output_path = f'example/outputs/{pessoa}_{modelname}.tex'
            
            start = timeit.default_timer()
            pipeline.run(input_path, output_path)
            end = timeit.default_timer()
            print(f'\nELAPSED TIME: {round(end-start,2)}s\n')