
def allow_tags(func):
    def _decorate(_func):
        _func.allow_tags = True
        return _func
    return _decorate(func)
