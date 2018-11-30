# -*- coding: utf-8 -*-


# $$\                $$\ $$\                       $$\
# $$ |               $$ |$$ |                      $$ |
# $$ |  $$\ $$$$$$\  $$ |$$ |$$\   $$\  $$$$$$$\ $$$$$$\    $$$$$$\
# $$ | $$  |\____$$\ $$ |$$ |$$ |  $$ |$$  _____|\_$$  _|  $$  __$$\
# $$$$$$  / $$$$$$$ |$$ |$$ |$$ |  $$ |\$$$$$$\    $$ |    $$ /  $$ |
# $$  _$$< $$  __$$ |$$ |$$ |$$ |  $$ | \____$$\   $$ |$$\ $$ |  $$ |
# $$ | \$$\\$$$$$$$ |$$ |$$ |\$$$$$$$ |$$$$$$$  |  \$$$$  |\$$$$$$  |
# \__|  \__|\_______|\__|\__| \____$$ |\_______/    \____/  \______/
#                            $$\   $$ |
#                            \$$$$$$  |
#                             \______/
#
# Copyright 2017 Barry Smnyth
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice & this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import re

def to_markdown(kmd_file, include_file):
    """Convert a Kallysto markdown file to a standard markdown file.
    
    Replace named definitions in the .kmd file with their corresponding 
    values based on the export defintions referenced by the include_file.
    The result is a new .md file with the same basename as the kmd_file and
    saved to the same directory as the kmd_file.
    
    Args:
        kmd_file: a source Kallysto markdown file with export references.
        include_file: a text file with a list of paths to export defintion files.
    """
    
    # Read the export definitions.
    defs_dict = include_defintions(include_file)
    
    # Replace the references in the kmd_file with the
    # corresponding definition and return the resulting md.
    md = replace_definitions(kmd_file, defs_dict)
    
    md_file = kmd_file.replace('.kmd', '.md')
    
    # Write to md file.
    with open(md_file, 'w+') as f:
        f.write(md)
    
    return md_file
    
    
def include_defintions(include_file):
    """Read in the Kallysto definitions referenced in the include_file.
    
    Args:
        include_file: a text file with a list of paths to export defintion files.
        
    Returns:
        A dict of definitions, {name:value}

    """
    
    defs_dict = {}
    path_to_include = os.path.split(include_file)[0]
    
    with open(include_file, 'r') as f:
        
        cwd = os.getcwd()
                
        # Read and parse each definitions file.
        for definitions_file in f.readlines():
            
            # Locate the definitions_file relative to the cwd.
            path_to_defs = os.path.relpath(
                path_to_include + '/' + definitions_file, start=cwd)
        
            defs_dict = read_definitions(path_to_defs, defs_dict)
        
        return defs_dict


def read_definitions(definitions_file, defs_dict):
    
    """Read in the defintions in the defintions file and add to the dict.
    
    Args:
        defintions_file: a file of kallysto defintions.
        
    Returns:
        An updated dict of definitions (name:value).
    
    """
            
    with open(definitions_file, 'r') as d:
        
        # Parse the defintions, extracting the name
        # and value and adding to dict.
        defs_str = parse_definitions(d.read(), defs_dict)
            
    return defs_dict

def parse_definitions(defs_str, defs_dict):
    """Extract defintion names and values from the defs_string and add to dict.
    
    Args:
        defs_str: string of Kallysto defintions.
        defs_dict: defintions dictionary
        
    Returns:
        Updated defintions dict with definitions found in defs_str.
    """
    
    for def_str in re.findall(r'\{(.*?)\}',defs_str, re.DOTALL):
        name, value = re.search(r'(.*?):(.*)', def_str, re.DOTALL).groups()
        
        defs_dict[name] = value    
            
    return defs_dict
                    
            
def replace_definitions(kmd_file, defs_dict):
    """Replace the defs in kmd_file with values in defs_dict.
    
    Find and replace each kallysto defintion in kmd_file (by name)
    with the corresponding value in defs_dict.
    
    Args:
        kmd_file: markdown file with Kallytso defintion references {name}.
        defs_dict: dict of name:value associations for defintions.
        
    Returns:
        Markdown string based on teh contents of kmd_file with defintion
        references replaced with corresponding values from defs_dict.
    """
    with open(kmd_file, 'r') as kmd:
        
        kmd_contents = kmd.read()
        
        # Pull out all of the references, {ref}
        refs = re.findall(r'\{(.*?)\}', kmd_contents, re.DOTALL)
        
        # Look to replace each ref found with its defs_dict value.
        for ref in refs:
            
            # If the ref is in the dict, replace it in the kmd.
            if ref in defs_dict:
                replace_with = defs_dict[ref]
                kmd_contents = kmd_contents.replace(
                    '{{{}}}'.format(ref), replace_with)
            
        return kmd_contents