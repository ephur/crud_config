def toBool(string):
    if str(string).upper() in ['YES', 'Y', '1', 'TRUE', 'T', 'YE']: return True
    if str(string).upper() in ['N', 'NO', 'FALSE', 'F', '0', "0.0", "[]", "{}", "None" ]: return False
    raise ValueError("Unknown Boolean Value")