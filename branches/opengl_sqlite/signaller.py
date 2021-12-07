# for passing signals around
handlers={}
def connect(objectFrom,signalName,method):
    if(signalName not in handlers):
        handlers[signalName]={}
    if(objectFrom not in handlers[signalName]):
        handlers[signalName][objectFrom]=[]
    handlers[signalName][objectFrom].append(method)
    pass
           
def emit(objectFrom,signalName,params=None):
    if(signalName in handlers):
        originDict=handlers[signalName]
        if(objectFrom in originDict):
            handlerList=originDict[objectFrom]
            for slot in handlerList:
                slot(objectFrom,params)
                pass
            pass
        if(None in originDict):
            handlerList=originDict[None]
            for slot in handlerList:
                slot(objectFrom,params)
                pass
            pass
        pass
    pass

