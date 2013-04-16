from model import *

sample = """
name: "Hello WebApp Cluster with Database"
components:
  # key here equivalent to supplying a map with this as the value for key 'id'
  hello_war:
    content: hello.war
    requires:
      com.example.java:WarDeploymentRequirement:
        fulfillment: id:frontend
  hello_sql:
    content: hello.sql
    type: com.example.database:Schema   # here, type of component defined
    requires: id:backend                # assume Schema defines default req type "DB"
  frontend:                             # "platform component" implied by WarDeplReq above
    requires:
      database:                         # frontend type must recognise a named "database" req
        mode: CDI                       # assume that req supports various injection modes
        fulfillment: id:backend
      com.example.lb:LoadBalanced:      # longhand req form: this is the 'type'
        protocol: https                 # assume that type recognises these attributes
        algorithm: round-robin
        sticky-sessions: true
        fulfillment: id:lb
  lb: { tags: [ "load-balancer" ] }     # tag it so we can monitor it afterwards
"""

def testFlatten():
    print flatten([[1, 2], [3], [4, 5]])
    assert flatten([[1, 2], [3], [4, 5]]) == [1, 2, 3, 4, 5]

def testRequirementAttributesAreSet():
    input = {
        'algorithm': 'round-robin',
        'fulfillment': 'id:lb',
        'protocol': 'https',
        'sticky-sessions': True
    }
    requirement = Requirement('com.example.lb:LoadBalanced', input)
    assert requirement.algorithm == 'round-robin'
    assert requirement.protocol == 'https'
    assert requirement.fulfilledBy == 'lb'

def testComponentAttributesAreSet():
    input = {
        'requires': {
            'com.example.lb:LoadBalanced': {
                'algorithm': 'round-robin',
                'fulfillment': 'id:lb',
                'protocol': 'https',
                'sticky-sessions': True
            },
            'database': {
                'fulfillment': 'id:backend', 'mode': 'CDI'
            }
        }
    }
    component = Component("frontend", input)
    assert len(component.requirements) == 2
    assert set(r.fulfilledBy for r in component.requirements) == set(['lb', 'backend'])

def testLoadBlueprint():
    blueprint = Blueprint(sample)
    assert blueprint.name == "Hello WebApp Cluster with Database"
    assert len(blueprint.components) == 4

    assert set(r.id for r in blueprint.requirements()) == set(
        ['com.example.lb:LoadBalanced', 'database', 'id:backend', 'com.example.java:WarDeploymentRequirement'])

