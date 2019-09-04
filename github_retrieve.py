# importing libraries
import sys
import os
import re
from itertools import islice
from git import Repo
from pathlib import Path
from url_read import urls_reader
from duplication import code_duplication_check


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


