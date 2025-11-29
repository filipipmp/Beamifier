import os

import PIL
from PIL import Image

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered



#==============================================================================================================
# CUSTOM CLASSES FOR EXTRACTING TEXT TO MARKDOWN
# Class for marker library
# TODO: ver necessidade de mais metodos para generalismo
class MARKER():
    def __init__(self):
        self.converter = PdfConverter(
            artifact_dict=create_model_dict(),
        )
    
    def convert(self, filename):
        rendered = self.converter(filename)
        self.text, _, self.images = text_from_rendered(rendered)

    # Nome sem extensao
    def save(self, filename="output"):
        if not os.path.exists(filename):
            os.makedirs(filename)
        # salva arquivo md
        with open(f'{filename}/{filename}.md','w') as f:
            f.write(self.text)
        # salva dicionario de imagens
        for name, image in self.images.items():
            image.save(f'{filename}/{name}')
#==============================================================================================================



if __name__=='__main__':
    conv = MARKER()
    conv.convert('paper.pdf')
    conv.save()