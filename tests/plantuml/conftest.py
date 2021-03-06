import pytest
from napkin import gen_plantuml
from napkin import sd


@pytest.fixture
def check_puml(tmpdir):
    def fn(sd_func, exp_lines):
        exp_lines = '@startuml' + exp_lines + '@enduml\n'
        sd_context = sd.parse(sd_func)
        puml_file = gen_plantuml.generate(str(tmpdir), 'test', sd_context)[0]
        with open(puml_file, 'rt') as f:
            lines = f.read()
        assert lines == exp_lines
    return fn
