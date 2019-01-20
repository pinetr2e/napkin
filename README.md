# Napkin 

Python as DSL for writing sequence diagram.

The sequence diagrams are useful tool to capture the S/W design and
[PlantUML](www.plantuml.com) is a great tool to write nice sequence diagrams in
plain text.

However, the syntax of PlantUML is quite error prone especially when there are
nested calls involved.

For example:
```
participant User

User -> Foo: DoWork()
activate Foo 

Foo -> Foo: InternalCall()
activate Foo

Foo -> Bar: CreateRequest()
activate Bar

Bar --> Foo: Request
deactivate Bar
deactivate Foo
deactivate Foo
```
By using normal Python code, it can be naturally expressed with 'with' statement as below:
```python
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
```
Basically, sequence diagram is expressed as methods calls between objects.

There are several advantages of using Python as DSL:
* Easy to write correct diagrams
* Many common mistakes are detected as normal Python error. For example, method
  call to an undefined object will be just normal Python error.
* Any Python editor can become sequence diagram editor


## Installation

Install and update using `pip`
```
pip install -U napkin
```

## Hello world

Write a simple script called hello.py as follows:

```python
import napkin

@napkin.seq_diagram
def hello_world(c):
    user = c.object('user')
    world = c.object('world')
    with user:
        world.hello()
```
Then, the following command will generate hello_world.uml:
```
$ napkin hello.py
```

## More examples
[See example](./demo/readme_examples.py)
