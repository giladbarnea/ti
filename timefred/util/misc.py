from timefred import color as c


def confirm(question):
    return input(f' {c.blue("?")} ' + question + c.b(' [y/n]  ')).lower() in ('y', 'yes')