import re


def is_valid_password(password):
    """ Validate passwords according to NIST SP 800-63B criteria """
    reg = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{12,25}$"
    pattern = re.compile(reg)
    match = re.search(pattern, password)
    print("match",match)
    if match:
        return True
    return False


def is_common_password(password):
    with open('common_password.txt', 'r', encoding='utf-8') as file:
        for compromised_password in file.readlines():
            if password == compromised_password:
                return False
    return True
