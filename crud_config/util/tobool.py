def toBool(string):
    falses = ['N', 'NO', 'FALSE', 'F', '0', "0.0", "[]", "{}", "NONE", ""]
    trues = ['YES', 'Y', '1', 'TRUE', 'T', 'YE']
    if str(string).upper() in trues:
        return True
    if str(string).upper() in falses:
        return False
    raise ValueError("Unknown Boolean Value %s" % (str(string).upper()))