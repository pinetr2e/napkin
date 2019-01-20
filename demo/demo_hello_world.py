import napkin


@napkin.seq_diagram()
def hello_world(c):
    user = c.object('user')
    world = c.object('world')
    with user:
        world.hello()
