import yaml
import os

class SwaggerCombiner:
    """Swagger combiner class"""

    _relative_dir = "."

    _files = []
    """list(str): list of filenames to combine"""

    def __init__(self):
        pass
    
    def set_relative_dir(self, relative_dir):
        self._relative_dir = relative_dir
    
    def set_files(self, files):
        self._files = files
        
    def combine(self, output_stream):
        self._files.sort()
        merged_obj = None
        for f in self._files:
            relative_f = os.path.join(self._relative_dir, f)
            with open(relative_f, "r") as stream:
                try:
                    obj = yaml.safe_load(stream)
                    if merged_obj is None:
                        merged_obj = obj
                    else:
                        self._merge(merged_obj, obj, f, "");
                except yaml.YAMLError as exc:
                    print(exc)
                    
        # Write YAML file
        #with io.open('data.yaml', 'w', encoding='utf8') as outfile:
        yaml.dump(merged_obj, output_stream, default_flow_style=False, allow_unicode=True)


    def _merge(self, merged_obj, obj, f, prefix):
        print("not implemented")
        
        
    def f(self):
        return 'hello world'

def add_one(number):
    return number + 1
