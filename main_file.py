import re
from github_retrieve import (
    traverse_repos,
    code_duplication_check,
    find_repo_imports,
    count_lines_of_code,
    find_for_loops,
    avarage_parameters,
    avarage_variables_per_line,
    find_docstrings_and_comments,
    find_external_packages,
    nesting_depth
)
def perform_calculations():
    """ 
    function helps looping once on each line to perform all operations 
    """
    # contains the result of the total repositories
    result = [] 
    count_all_lines = 0 # mainatains the line that has been counted
    for_loops_list = []
    func_parameters = [] # function parameter checks list
    no_of_variables = set() # a set containing variables
    docs_comments = []  
    single_line_comments = []
    code_duplication = 0
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

    return result
print(perform_calculations()) # make it return stuffs