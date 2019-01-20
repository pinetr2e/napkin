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


@napkin.seq_diagram()
def hello_world(c):
    user = c.object('user')
    world = c.object('world')
    with user:
        world.hello()

if __name__ == '__main__':
    napkin.generate()
