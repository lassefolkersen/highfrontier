import sys
import importlib
# sys.setdefaultencoding may be deleted by site.py, 
# so bring it back:
importlib.reload(sys)
if hasattr(sys,"setdefaultencoding"):
    sys.setdefaultencoding("latin-1")
    print("did it")