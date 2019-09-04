# importing libraries
import sys
import os
import re
from itertools import islice
from git import Repo
from pathlib import Path
from url_read import urls_reader
# research on reseting or freeing resources once a file closed-
result = []



def single_line_in_file():
    """ 
    function helps looping once on each line to perform all operations 
    """
    count_all_lines = 0
    for_loops_list = []
    func_parameters = []
    no_of_variables = set()
    docs_comments = []
    single_line_comments = []
    code_duplication = 0
    all_repos_result = []
    repo_imports_set = set() # imports for the entire repo
    current_repo = ''
    for item in traverse_repos():
        current_repo = item['repo_url']
        for path in item['files']:
            with open(path, 'r') as file_:
                lines = file_.readlines()
                # call code duplication
                code_duplication  += code_duplication_check(lines)
                for line in lines:
                    if re.match(r'^#.+', line.strip()):
                        single_line_comments.append(line.strip())
                        # this makes it possible to campare later
                    # call find_repo_imports
                    line_import = find_repo_imports(line)
        
                    repo_imports_set.add(line_import)
                    # call countlines of code function
                    count_all_lines += count_lines_of_code(line.strip())
                    # call find_for_loops
                    for_loops = find_for_loops(line)
                    if for_loops:
                        for_loops_list.append(for_loops)
                    function = avarage_parameters(line)
                    if function:
                        func_parameters.append(avarage_parameters(line))
                    no_of_variables.add(avarage_variables_per_line(line))
        
            with open(path, 'r') as content_file:
                content = content_file.read()
                docs_comments.extend(find_docstrings_and_comments(content, single_line_comments))
        external_packages = find_external_packages(repo_imports_set)
        repo_lines_of_codes = count_all_lines - len(docs_comments)
        avarage_variables_repo = (len(no_of_variables)-1) / repo_lines_of_codes
        nesting = nesting_depth(for_loops_list) / len(for_loops_list)
        avarage_params = sum(func_parameters) / len(func_parameters)
        repo_result = {
                    'repository_url': current_repo, 
                    'number of lines': repo_lines_of_codes, 
                    'libraries': external_packages,
                    'nesting factor': nesting,
                    'code duplication': code_duplication,
                    'average parameters': avarage_params,
                    'average variables': avarage_variables_repo
                
            }
        result.append(repo_result)
    

def generate_file_path(directory, filename=None):
    if filename:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), directory,filename)
    else:  
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), directory)
    return path


def traverse_repos():
    repo_paths = []
    try:
        urls = urls_reader()
        for url in urls:
            repo_dir = url.split('/')[-1]
            repo_paths.append({'repo_path':generate_file_path(repo_dir),'url':url})
            try:
                Repo.clone_from(url, repo_dir)
            except:
                continue
        
    except Exception as e:
        print("An error occured.", e)
    finally:
        
        # repo_python_files are all .py the files in a single github repository
        exclude_dirs = ['.git']
    
        for repo_path in repo_paths:
            for (root, dirs, files) in os.walk(repo_path['repo_path'], topdown=True):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                files[:] = [generate_file_path(root, f) for f in files if f.lower().endswith('.py')]        
            yield {'files':files,'repo_url':repo_path['url']}
       

def find_docstrings_and_comments(file_, single_line_comments):
    docstrings = re.findall(r'"""[\s\S]*?"""', file_)
    return [*docstrings, *single_line_comments]


def count_lines_of_code(line):
    line_code = 0
  
    if line.strip():
        line_code += 1

    return line_code

def find_repo_imports(line):
    """lines : lines from readlines() function"""
    line_import = None
    if line.strip().startswith('import'):
        line_import = line.strip().split(' ')[1]
    elif line.strip().startswith('from') and 'import' in line:
        line_import = line.strip().split(' ')[1]
    return line_import
        

def find_external_packages(repo_imports_set): # note import bs4 external packAGES NOT  working
    """finds the external packages
       repo_imports_set(set): a set containing all imports in individual repo file
    """
    external_packages = []
    try:
        paths = (os.path.abspath(p) for p in sys.path)
        external_paths_gen= [p for p in paths if 'site-packages' in p]
        external_paths_set = set(external_paths_gen)
        # remove any None returned as a result of a line not being an import statement

        repo_imports_set.remove(None)
        site_package_path_gen = (path.split('site-packages')[0]+'site-packages' for path in external_paths_set)
        
        external_libs_gen = (
            os.path.join(p, package) for p in site_package_path_gen for package in repo_imports_set)
        for file_path in set(external_libs_gen):
            file_ = Path(file_path)
            if file_.is_file() or file_.is_dir():
                external_packages.append(str(file_).split('/')[-1])

        return external_packages
        
        
    except Exception:
        raise



def find_for_loops(line):
    """[counts nesting for for loops]
    
    Arguments:F
        line {string} -- [the current line returned from readline]
    """
    if line.strip().split(' ')[0] == 'for' \
        or('range' or 'xrange' or 'enumerate' or 'in') in line \
        and ':' in line:
        return  1,len(line.split('for')[0])
    return 0

def nesting_depth(for_loops_list):
    """[summary]
    
    Arguments:
        for_loops_list {[list]} -- [a list of for loops in aa single repo]
    
    Returns:
        [int] -- [an incremented value each time for loop is found]
    """
    try:
        min_identation = min(for_loops_list)
        count_indentation = 0

        for item in for_loops_list:
            if item[1] - min_identation[1] ==  0 :
                count_indentation += 1
            elif item[1] - min_identation[1] >=  min_identation[1]:
                count_indentation += 1

        return count_indentation
    except Exception as e:
        print('An error accure', e)


def avarage_parameters(line):
    """[checks and return the avarage number of parameters]
    
    Arguments:
        line {[str]} -- [the current line returned from readline]
    """
    functions = line.strip()
    if line.strip().split(' ')[0] == 'def':
        return len(functions.split('(')[1].split(','))

def avarage_variables_per_line(line):
    """[calculates the avarage variables per repository]
    
    Arguments:
        line {[str]} -- [the current line returned from readline]
    """
    
    is_variable = line.strip().split('=')

    if len(is_variable) == 2 and ('+=' or '-=' or '*' or '/' or '['or']') not in line.strip().split(' '):
        return is_variable[0]
    return None

def code_duplication_check(lines):
    """[check the a file for code duplication]
    
    Arguments:
        file_ {[str]} -- [content of the current file]
    """
    # get indexes of all '""""' 
    lines = [
        line.strip() for line in lines if len(line.strip())>0 and not re.match(r'^#.+', line.strip())]
    docstrings_remove_final = []
    docstrings_remove = []
    # get indexes of all '"""'
    idx = [i for i,v in enumerate(lines) if v in ([ '"""'] or "'''")]
    for i in range(len(idx)): 
        if i%2==0 and len(idx) > 2:
            idx[i] = idx[i]+1
            docstrings_remove.extend([lines[idx[index]:idx[index+1]] for index in range(0, len(idx)-1,2)])
        elif i%2==0 and len(idx) == 2:
            docstrings_remove.extend([lines[idx[0]:idx[1]] for index in range(0, len(idx)-1,2)])
    # list of docstrings to be removed
    #docstrings_remove = [lines[idx[index]:idx[index+1]][0] for index in range(0, len(idx)-1,2)]
    for item in docstrings_remove:
        for docs in item:
            docstrings_remove_final.append(docs) 
    lines = [
        item.strip() for item in lines if item not in docstrings_remove and not\
                (item.startswith('"""') or item.startswith("'''"))]
    file_str = ''
    count = 0
    line_length = 0
    while line_length <= len(lines)-1:
        if count < 4:    
            file_str += lines[line_length]
            count += 1
        elif count == 4:
            file_str += '<~>'
            count = 0

        line_length += 1

    file_list = file_str.split('<~>')
    file_list[:] = [s for s in file_list if len(s.strip())>0]
    duplicates = len(file_list) - len(set(file_list))
    return 2
    
single_line_in_file() # make it return stuffs
print(result)
