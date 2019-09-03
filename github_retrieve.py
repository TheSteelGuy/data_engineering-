# importing libraries
import sys
import os
import re
from itertools import islice
from git import Repo
from pathlib import Path
# resech on reseting or freeing resources once a file closed-
result = []
repo_imports_set = set() # imports for the entire repo

def single_line_in_file():
    """ 
    function helps looping once on each line to perform all operations 
    """
    count_all_lines = 0
    for_loops_list = []
    func_parameters = []
    no_of_variables = 0
    docs_comments = []
    single_line_comments = []

    repo_python_files = traverse_repos() # repo_python_files(list): all .py files in a repo
    for path in repo_python_files:
        with open(path, 'r') as file_:
            lines = file_.readlines()
            # call code duplication
            code_duplication_check(lines, path)
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
                no_of_variables += avarage_variables_per_line(line)
        file_.close()
        
        with open(path, 'r') as content_file:
            content = content_file.read()
            docs_comments.extend(find_docstrings_and_comments(content, single_line_comments))
        content_file.close()

    repo_lines_of_codes = count_all_lines - len(docs_comments)
    # nesting = nesting_depth(for_loops_list) / len(for_loops_list)
    avarage_params = sum(func_parameters) / len(func_parameters)
    avarage_variables_repo = no_of_variables / repo_lines_of_codes
    print('repo_lines_of_codes', repo_lines_of_codes)    
    print('func_parameter_av',avarage_params)
    print('avarage_variables_repo ', avarage_variables_repo )
    
    # # print('nesting', nesting)
    
    # return repo_lines_of_codes



def generate_file_path(directory, filename=None):
    if filename:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), directory,filename)
    else:  
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), directory)
    return path


def traverse_repos():
    try:
        url = "https://github.com/bitly/data_hacks"
        repo_dir = url.split('/')[-1]
        #Repo.clone_from(url, repo_dir)
        repo_path = generate_file_path(repo_dir)
        exclude_dirs = ['.git']
        # repo_python_files are all .py the files in a single github repository
        repo_python_files = []
        for (root, dirs, files) in os.walk('collo', topdown=True):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            files[:] = [generate_file_path(root, f) for f in files if f.lower().endswith('.py')]
            repo_python_files.extend(files)

        return repo_python_files

    except Exception as e:
        print("An error occured.", e)

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
    line_import = ''
    if line.strip().startswith('import') \
        or (line.strip().startswith('from') and 'import' in line):
        if len(line.split(' ')[1].split('.')) == 1:
            line_import = line.split(' ')[1]
        else:
            line_import= line.split(' ')[1].split('.')[0]
        return line_import

def find_external_packages(repo_imports_set): # note import bs4 external packAGES NOT  working
    """finds the external packages
       repo_imports_set(set): a set containing all imports in individual repo file
    """
    try:
        paths = (os.path.abspath(p) for p in sys.path)
        external_paths_gen= [p for p in paths if 'site-packages' in p]
        external_paths_set = set(external_paths_gen)
        repo_imports_set.remove(None)
        site_package_path_gen = (path.split('site-packages')[0]+'site-packages' for path in external_paths_set)
        external_libs_gen = (
            os.path.join(p, package) for p in site_package_path_gen for package in repo_imports_set)
        external_packages = 0
        for file_path in set(external_libs_gen):
            file_ = Path(file_path)
            if file_.is_file() or file_.is_dir():
                external_packages += 1
        
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
    if len(is_variable) == 2:
        return 1
    return 0

def code_duplication_check(lines, path):
    """[check the a file for code duplication]
    
    Arguments:
        file_ {[str]} -- [content of the current file]
    """
    # get indexes of all '""""' 

    with open(path, 'r') as infile:
        content = infile.read()
        infile.close()

        lines = [
            line.strip() for line in lines if len(line.strip())>0 and not re.match(r'^#.+', line.strip())]
        print('lines lines.....', lines)
        docstrings_remove = ''
        # get indexes of all '"""'
        idx = [i for i,v in enumerate(lines) if v in ([ '"""'] or "'''")]
        for i in range(len(idx)): 
            if i%2==0 and len(idx) > 2:
                idx[i] = idx[i]+1
                docstrings_remove = [lines[idx[index]:idx[index+1]][0] for index in range(0, len(idx)-1,2)]
            elif i%2==0 and len(idx) == 2:
                docstrings_remove = [lines[idx[0]:idx[1]] for index in range(0, len(idx)-1,2)]
            #continue
        print('.....idx', idx)
        # list of docstrings to be removed
        #docstrings_remove = [lines[idx[index]:idx[index+1]][0] for index in range(0, len(idx)-1,2)]
        lines = [
            item.strip() for item in lines if item not in docstrings_remove[0] and not\
                 (item.startswith('"""') or item.startswith("'''"))]
        #print('docstringd to remove', docstrings_remove)
        #docstrings_remove = [lines[idx[index]:idx[index+1]][0] for index in range(0, len(idx)-1,2)]
        print('docstringd to remove', docstrings_remove)
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

        print('dublicates.......', lines)
    
 


        



single_line_in_file() # make it return stuffs
print(find_external_packages(repo_imports_set), 'yes')
#print(';;;;;>>>>>',repo_imports_set)
#print(external_libs('k'))
# (1,4)(4,8)
