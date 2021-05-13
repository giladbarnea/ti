from ti import color as c
def confirm(question):
    return input(question + c.b(' [yn]  ')).lower() in ('y', 'yes')
