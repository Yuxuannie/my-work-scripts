def load_list(path, trim=True):
    with open(path, 'r') as f:
        lst = f.readlines()
    if trim:
        lst = filter(None, (map(str.strip, lst)))
    lst = list(lst)
    return lst
 
