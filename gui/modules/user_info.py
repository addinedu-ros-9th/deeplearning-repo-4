user_id = ''
user_info = {'name': '', 'email': '', 'store_name': ''}

def set_user_id(id):
    global user_id
    if id != '':
        user_id = id
    else:
        print("No user id")
        user_id = ''

def set_user_info(info):
    global user_info
    if info['name'] != '':
        user_info = info
    else:
        print("No user found with the given user_id.")
        user_info = {'name': '', 'email': '', 'store_name': ''}

def get_user_id():
    return user_id

def get_user_info():
    return user_info

def reset_user():
    global user_id
    global user_info
    user_id = ''
    user_info = {'name': '', 'email': '', 'store_name': ''}