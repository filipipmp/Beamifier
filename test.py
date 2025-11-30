from src.pipeline import Beamifier_Pipeline
from src.summarizer import summarizers_dict

import os
import timeit

if __name__=='__main__':
    pessoas = [
        "marcos",
        "guilherme"
    ]
    api_key = os.environ['API_KEY']

    for modelname in summarizers_dict.keys():
        pipeline = Beamifier_Pipeline(model=modelname, api_key=api_key, _compile=True, remove_trash=True)
        for pessoa in pessoas:
            input_path  = f'example/{pessoa}/main.tex'
            output_path = f'example/outputs/{pessoa}_{modelname}.tex'
            
            start = timeit.default_timer()
            pipeline.run(input_path, output_path)
            end = timeit.default_timer()
            print(f'\nELAPSED TIME: {round(end-start,2)}s\n')