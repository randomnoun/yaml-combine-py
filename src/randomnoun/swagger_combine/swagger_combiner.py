import yaml
import os
import logging
import sys
from urllib.parse import unquote


class SwaggerCombiner:
    """Swagger combiner class"""

    _relative_dir = "."

    _verbose = False

    _files = []
    """list(str): list of filenames to combine"""

    _yaml_files = {}
    """YAML file cache"""

    def __init__(self):
        self._yaml_files = {}
        self._files = []
        self._verbose = False
        self._relative_dir = "."
        pass

    def set_relative_dir(self, relative_dir):
        self._relative_dir = relative_dir

    def set_files(self, files):
        self._files = files

    def set_verbose(self, verbose):
        self._verbose = verbose

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
                        self._merge(merged_obj, obj, f, "")
                except yaml.YAMLError as exc:
                    print(exc)

        self._replace_refs(merged_obj, self._relative_dir, "")

        # formatting improvements as per
        # https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
        def str_representer(dumper, data):
            if len(data.splitlines()) > 1:  # check for multiline string
                return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
            return dumper.represent_scalar("tag:yaml.org,2002:str", data)

        yaml.add_representer(str, str_representer)

        # yaml.dump() doesn't include the directives separator
        # include it for compatibility with the java swagger-combine output
        output_stream.write("---\n")

        # For Python 3.7+, dicts preserve insertion order.
        # so let's sort in py 3.6, and not sort in py 3.7
        is_py37 = sys.version_info >= (3, 7, 0)
        yaml.dump(
            merged_obj, output_stream, default_flow_style=False, allow_unicode=True, sort_keys=not is_py37
        )

    def _merge(self, merged_obj, obj, f, prefix):
        clone_list = list(obj.keys())
        for k in clone_list:
            v = obj[k]
            mv = merged_obj.get(k)
            if mv is None:
                # simple merge
                merged_obj[k] = v
            elif v is None:
                # nothing to merge
                pass
            elif isinstance(mv, dict) and isinstance(v, dict):
                # the only thing we can merge are dictionaries
                self._merge(mv, v, f, prefix + str(k) + "/")
            elif type(mv) is type(v):
                # replace if the types are the same
                merged_obj[k] = v
            else:
                raise ValueError("Could not merge " + f + "#" + prefix + str(k) +
                      " (" + str(type(v)) + ") into merged object " + str(type(mv)))

    def _replace_refs(self, obj, relative_dir, space_prefix):
        result = None
        if "$xref" in obj:
            xref = obj["$xref"]
            if self._verbose:
                logging.info(space_prefix + "$xref to " + xref)
            result = self._get_xref(relative_dir, xref)
            if isinstance(result, dict):
                # shallow clone, but _replace_refs will perform shallow clones at deeper levels
                result = result.copy()
                result = self._replace_refs(result, relative_dir, space_prefix + "  ")
            for k in obj.keys():
                v = obj[k]
                if k == "$xref":
                    # ignore
                    pass
                else:
                    if self._verbose:
                        logging.info(space_prefix + str(k))
                    if isinstance(result, dict):
                        r = result
                        if k not in r:
                            # add new property to xref'ed dictionary
                            r[k] = v
                        elif isinstance(r[k], dict) and isinstance(v, dict):
                            # the xref'ed object is a dictionary containing a dictionary
                            # don't think this is ever going to happen. but maybe it will
                            rv = r[k]
                            self._merge(rv, v, "", str(k) + "/")
                        else:
                            # replace existing key/value pairs
                            r[k] = v
                    else:
                        raise ValueError("Could not override " + str(k) +
                                         " (" + str(type(v)) + ") from xref '" + xref + "' " +
                                         str(type(result)))
        else:
            # descend into obj
            clone_list = list(obj.keys())
            for k in clone_list:
                v = obj[k]
                if k == "$xref":
                    raise ValueError("$xref found in dictionary that didn't contain $xref")
                elif self._verbose:
                    logging.info(space_prefix + str(k))
                if isinstance(v, dict):
                    # shallow clone, but _replace_refs will perform shallow clones at deeper levels
                    clone = v.copy()
                    new_object = self._replace_refs(clone, relative_dir, space_prefix + "  ")
                    obj[k] = new_object
            result = obj

        return result

    def _get_xref(self, relative_dir, ref):
        # myproject-v1-object.yaml#/definitions/InvalidResponse       existing
        # myproject-v1-swagger-api.yaml#/paths/~1authenticate         the JSON-Pointer way
        # myproject-v1-swagger-api.yaml#/paths/%2Fauthenticate        the url escape way
        # myproject-v1-swagger-api.yaml#/paths/#/authenticate         the randomnoun way.

        # can't have '#' as the start of a key as that's a comment. but you probably can. somehow.
        pos = ref.find("#")
        if pos == -1:
            # local refs still start with a '#'
            # $ref: '#/paths/~1blogs~1{blog_id}~1new~0posts'
            raise ValueError("Unparseable $xref '" + str(ref) + "'")
        else:
            f = ref[0:pos]
            p = ref[pos + 1 :]
            result = ""
            as_json_path = True
            for ch in p:
                if ch == "#":
                    as_json_path = not as_json_path
                elif as_json_path:
                    result = result + ch
                else:
                    # escape this jsonpath-ly
                    if ch == "/":
                        result = result + "~1"
                    elif ch == "~":
                        result = result + "~0"
                    else:
                        result = result + ch
            ref = f + "#" + result

            # as per ResolverCache
            # although ResolverCache parses an entire json doc every time there's a ref,
            # even if we've already parsed it.

            ref_parts = ref.split("#/")
            file = ref_parts[0]
            definition_path = ref_parts[1] if len(ref_parts) == 2 else None

            contents = self._yaml_files.get(file)
            if contents is None:
                relative_f = os.path.join(relative_dir, file)
                with open(relative_f, "r") as stream:
                    try:
                        contents = yaml.safe_load(stream)
                    except yaml.YAMLError as exc:
                        raise ValueError("Invalid YAML file '" + relative_f + "'") from exc
                self._yaml_files[file] = contents

            if self._verbose:
                logging.info("definitionPath '" + definition_path + "' in '" + file + "'")

            if definition_path is None:
                return contents
            else:
                json_path_elements = definition_path.split("/")
                node = contents
                for json_path_element in json_path_elements:
                    try:
                        node = node[self._unescape_pointer(json_path_element)]
                    except BaseException:
                        raise ValueError("Could not descend into " + json_path_element +
                                         " of " + definition_path + " in contents of " + file)
                    if node is None:
                        raise ValueError("Could not find '" + definition_path + "' in contents of " + file)
                return node

    def _unescape_pointer(self, json_path_element):
        # URL decode the fragment
        # hopefully this is the python equivalent of URLDecoder.decode()
        json_path_element = unquote(json_path_element)
        # Unescape the JSON Pointer segment using the algorithm described in RFC 6901,
        # section 4: https://tools.ietf.org/html/rfc6901#section-4
        # First transform any occurrence of the sequence '~1' to '/'
        json_path_element = json_path_element.replace("~1", "/")
        # Then transforming any occurrence of the sequence '~0' to '~'.
        json_path_element = json_path_element.replace("~0", "~")
        return json_path_element
