import sys, inspect, importlib
sys.path.insert(0, '.')
from crewai.tools import BaseTool
mod = importlib.import_module('chart_generator_tool')
print('Modulo:', mod)
print('Dir:', [x for x in dir(mod) if not x.startswith('__')])
found_classes = [(name, obj) for name, obj in inspect.getmembers(mod) if inspect.isclass(obj) and issubclass(obj, BaseTool) and obj is not BaseTool]
print('Classi trovate:', found_classes)
