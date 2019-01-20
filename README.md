# Napkin 

Python as DSL for writing Plantuml sequence diagram.

The sequence diagrams are useful tool to capture the S/W design and
[[www.plantuml.com][PlantUML]] is a great tool to write nice sequence diagrams
using plain text.

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
@napkin.seq_diagram
def sd_test(c):   # 'c' is API to access Napkin
    user = c.object('User')
    foo = c.object('Foo')
    bar = c.object('Bar')

    with user:
        with foo.DoWork():
            with foo.InternalCall():
                with bar.CreateRequest():
                c.ret('Done')
```
It basically, defines objects and write a code expressing the same thing.

There are several advantages of using Python as DSL:
* Easy to write correct diagrams with nested calls and .
* Many common mistakes are detected as normal Python error. For example, method
  call to an undefined object will be just normal Python error. 
* Any Python editor can be used as it is simply normal Python code.


## Examples

Calls With return value:
```python
    foo = c.object('foo')
    bar = c.object('bar')

    with foo:
        bar.func().ret('something')
```

Pass other object:
```python
    foo = c.object('foo')
    bar = c.object('bar')
    baz = c.object('baz')

    with foo:
        bar.DoSomething(baz, "other value")
```

Loop:
```python
    foo = c.object('foo')
    bar = c.object('bar')

    with c.loop():
        with foo:
            bar.func()
```
Alt:
```python
    foo = c.object('foo')
    bar = c.object('bar')
    baz = c.object('baz')

    with c.alt():
        with c.choice('ok'):
            with foo:
                bar.func()
        with c.choice('else'):
            with foo:
                baz.func()
```
Create objects:
```python
    foo = c.object('foo')
    bar = c.object('bar')
    with foo:
        c.create(bar)
```

Destroy objects:
```python
    foo = c.object('foo')
    bar = c.object('bar')
    with foo:
        bar.func()
        c.destroy(bar)
```
