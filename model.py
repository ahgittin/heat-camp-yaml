import yaml
import sys
import itertools

def flatten(listoflists):
    return list(itertools.chain(*listoflists))


class Component(object):
    """
    e.g.
      hello_sql:
        content: hello.sql
        type: com.example.database:Schema
        requires: id:backend
    """
    def __init__(self, name, component):
        self.id = name
        self.tags = component.pop('tags', [])

        requirements = component.pop('requires', None)
        if isinstance(requirements, str):
            self.requirements = set([Requirement(requirements, {}, component=self)])
        elif isinstance(requirements, dict):
            self.requirements = set(Requirement(name, req, component=self) for name, req in requirements.iteritems())
        else:
            self.requirements = []

        # Set remaining values as attributes
        self.__dict__.update(component)


class Requirement(object):
    """
    e.g.
      database:
        mode: CDI
        fulfillment: id:backend
    """
    def __init__(self, id, data, component=None):
        self.id = id
        self.component = component
        fulfilledBy = data.pop('fulfillment', None)
        if fulfilledBy:
            # drop id: from start of string
            self.fulfilledBy = fulfilledBy[3:]

        # Set remaining values as attributes
        self.__dict__.update(data)

    def requiredBy(self):
        return self.component


class Blueprint(object):
    def __init__(self, source):
        model = yaml.safe_load(source)
        # Let's assume the source was sensible
        self.name = model['name']
        self.components = {}
        for name, data in model['components'].iteritems():
            self.components[name] = Component(name, data)

    def requirements(self):
        return flatten([component.requirements for component in self.components.values()])


if __name__ == "__main__":
    # 1 arg: stdin. 2 args: filename.
    if len(sys.argv) == 1:
        spec = Blueprint(sys.stdin.read())
    elif len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as f:
            spec = Blueprint(f)
    else:
        print "Usage: %s <filename or stdin>" % (sys.argv[0],)
        sys.exit(1)

    print spec.components

