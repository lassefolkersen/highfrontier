# for passing signals around
handlers={}
def connect(objectFrom,signalName,method):
    if(not handlers.has_key(signalName)):
        handlers[signalName]={}
    if(not handlers[signalName].has_key(objectFrom)):
        handlers[signalName][objectFrom]=[]
    handlers[signalName][objectFrom].append(method)
    pass
           
def emit(objectFrom,signalName,params=None):
    if(handlers.has_key(signalName)):
        originDict=handlers[signalName]
        if(originDict.has_key(objectFrom)):
            handlerList=originDict[objectFrom]
            for slot in handlerList:
                slot(objectFrom,params)
                pass
            pass
        if(originDict.has_key(None)):
            handlerList=originDict[None]
            for slot in handlerList:
                slot(objectFrom,params)
                pass
            pass
        pass
    pass

