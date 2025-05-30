def allowed_file(f):
    return '.' in f and \
           f.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}