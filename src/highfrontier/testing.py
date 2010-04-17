import sys
# sys.setdefaultencoding may be deleted by site.py, 
# so bring it back:
reload(sys)
if hasattr(sys,"setdefaultencoding"):
    sys.setdefaultencoding("latin-1")
    print "did it"