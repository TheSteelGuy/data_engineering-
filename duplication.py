import re
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
    line_string = ''
    for line in lines:
        line_string += ''.join(line.strip().split(' '))
    # print(line_string)

    # print('lines', lines) 
    # file_str = ''
    # count = 0
    # line_length = 0
    # while line_length <= len(lines)-1:
    #     if count < 4:    
    #         file_str += lines[line_length]
    #         count += 1
    #     elif count == 4:
    #         file_str += '<~>'
    #         count = 0

    #     line_length += 1

    # file_list = file_str.split('<~>')
    # file_list[:] = [s for s in file_list if len(s.strip())>0]
    # duplicates = len(file_list) - len(set(file_list))
    return 1 #duplicates