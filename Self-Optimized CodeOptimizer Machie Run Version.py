import re,ast,sys,inspect
from typing import Dict,Optional,Tuple
from memory_profiler import memory_usage
class CodeOptimizer:
 def __init__(self,debug:bool=False):
  self.debug=debug
  self.cache={}
 def strip_comments(self,code:str)->str:
  code=re.sub(r'"""[\s\S]*?"""','',code)
  code=re.sub(r"'''[\s\S]*?'''","",code)
  lines=[]
  for line in code.split('\n'):
   if'"""'in line or"'''"in line:lines.append(line);continue
   comment_pos=line.find('#')
   if comment_pos!=-1:
    if not any(line[:comment_pos].count(q)%2==1 for q in['"',"'"]):line=line[:comment_pos]
   lines.append(line)
  return'\n'.join(lines)
 def optimize_spaces(self,code:str)->str:
  lines=[]
  current_indent=0
  for line in code.split('\n'):
   stripped=line.strip()
   if not stripped:continue
   if stripped.startswith(('def ','class ','if ','elif ','else:','try:','except ','finally:','with ','while ','for ')):
    lines.append(' '*current_indent+stripped)
    current_indent+=4
   elif stripped=='pass':
    lines.append(' '*(current_indent-4)+stripped)
    current_indent-=4
   else:lines.append(' '*current_indent+stripped)
  return'\n'.join(lines)
 def validate_code(self,code:str)->Tuple[bool,Optional[str]]:
  try:ast.parse(code);return True,None
  except SyntaxError as e:return False,str(e)
 def optimize_runtime(self,code:str)->str:
  code=self.strip_comments(code)
  code=self.optimize_spaces(code)
  code=re.sub(r'\s+',' ',code)
  code=re.sub(r'\s*([{}:,()])\s*',r'\1',code)
  is_valid,error=self.validate_code(code)
  if not is_valid:raise ValueError(f"Optimization produced invalid code: {error}")
  return code
 def measure_memory(self,code:str)->float:
  def code_runner():exec(code)
  mem_usage=memory_usage((code_runner,(),{}),max_iterations=1)
  return max(mem_usage)if mem_usage else 0.0
 def create_dual_versions(self,hr_code:str,module_name:str)->Dict[str,str]:
  mr_code=self.optimize_runtime(hr_code)
  hr_path=f"{module_name}_hr.py"
  mr_path=f"{module_name}_mr.py"
  with open(hr_path,'w')as f:f.write(hr_code)
  with open(mr_path,'w')as f:f.write(mr_code)
  return{'hr_path':hr_path,'mr_path':mr_path,'memory_usage':self.measure_memory(mr_code)}
def optimize_on_load(module_name:str):
 def decorator(func):
  optimizer=CodeOptimizer()
  def wrapper(*args,**kwargs):
   source=inspect.getsource(func)
   optimized=optimizer.optimize_runtime(source)
   exec(optimized)
   return locals()[func.__name__](*args,**kwargs)
  return wrapper
 return decorator
