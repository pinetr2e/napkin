import napkin


@napkin.seq_diagram()
def sd_simple(c):
    user = c.object('User')
    foo = c.object('Foo')
    bar = c.object('Bar')

    with user:
        with foo.DoWork():
            with foo.InternalCall():
                with bar.CreateRequest():
                    c.ret('Done')


if __name__ == '__main__':
    napkin.generate()
