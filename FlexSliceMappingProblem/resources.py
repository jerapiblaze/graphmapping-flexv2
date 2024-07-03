from contextlib import ContextDecorator
from contextlib import contextmanager
from types import UnionType
import numpy as np
from collections.abc import Iterable


class NodeResource:   
    @property
    def cpu(self) -> np.float32:
        return self.resources[0]
    @property
    def memory(self) -> np.float32:
        return self.resources[1]
    @property
    def storage(self) -> np.float32:
        return self.resources[2]
    def __init__(self, cpu:np.float32=None, memory:np.float32=None, storage:np.float32=None):
        cpu = 0 if cpu is None else cpu
        memory = 0 if memory is None else memory
        storage = 0 if storage is None else storage
        self.resources=np.array([cpu, memory, storage])
        
    @classmethod
    def fromArray(self, arr:np.ndarray):
        t = NodeResource()
        t.resources = arr
        return t
        
    def __copy__(self):
        clone = NodeResource()
        clone.resources = self.resources
        return clone
    
    def __deepcopy__(self, memo):
        clone = NodeResource()
        clone.resources = self.resources
        return clone
    
    def __reduce__(self) -> tuple[object, tuple[np.float32,np.float32,np.float32]]:
        return (self.__class__, (self.cpu, self.memory, self.storage))
        
    def __len__(self) -> int:
        return len(self.resources)
        
    def __repr__(self) -> str:
        s = f"NodeResources(cpu={self.cpu}|memory={self.memory}|storage={self.storage})"
        return s
    
    def __add__(self, __value: object):
        c = NodeResource()
        c.resources = self.resources + __value.resources
        return c
    
    def __add__(self, __value: int):
        c = NodeResource()
        c.resources = self.resources + __value
        return c
    
    def __radd__(self, __value: int):
        c = NodeResource()
        c.resources = self.resources + __value
        return c
    
    def __sub__(self, __value: object):
        c = NodeResource()
        c.resources = self.resources - __value.resources
        return c
    
    def __sub__(self, __value: int):
        c = NodeResource()
        c.resources = self.resources - __value
        return c
    
    def __rsub__(self, __value: int):
        c = NodeResource()
        c.resources = __value - self.resources
        return c
    
    def __mul__(self, __value: int):
        c = NodeResource()
        c.resources = self.resources * __value
        return c
    
    def __rmul__(self, __value: int):
        c = NodeResource()
        c.resources = self.resources * __value
        return c
    
    def __truediv__(self, __value: int):
        c = NodeResource()
        c.resources = self.resources / __value
        return c
    
    def __round__(self, ndigits: int=None):
        c = NodeResource()
        c.resources = np.round(self.resources, decimals=0 if ndigits is None else ndigits)
        return c
    
    def __eq__(self, __value: object) -> bool:
        if ((type(__value) == int) and (__value == 0)):
            return self.resources == __value
        return all(self.resources == __value.resources)
    
    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)
    
    def __le__(self, __value:object) -> bool:
        res = []
        for i in range(len(self.resources)):
            if self.resources[i] == __value.resources[i]:
                continue
            res.append(self.resources[i] <= __value.resources[i])
        return any(res) if len(res) else True
        
    def __lt__(self, __value:object) -> bool:
        res = []
        if ((type(__value) == int) and (__value == 0)):
            return any(self.resources < __value)
        for i in range(len(self.resources)):
            if self.resources[i] == __value.resources[i]:
                continue
            res.append(self.resources[i] < __value.resources[i])
        return any(res) if len(res) else True
    
    def __ge__(self, __value:object) -> bool:
        res = []
        for i in range(len(self.resources)):
            if self.resources[i] == __value.resources[i]:
                continue
            res.append(self.resources[i] >= __value.resources[i])
        return all(res) if len(res) else True
    
    def __gt__(self, __value:object) -> bool:
        res = []
        for i in range(len(self.resources)):
            if self.resources[i] == __value.resources[i]:
                continue
            res.append(self.resources[i] > __value.resources[i])
        return all(res) if len(res) else True
    
    # def __le__(self, __value:object) -> bool:
    #     res = []
    #     for i in range(len(self.resources)):
    #         if self.resources[i] == __value.resources[i]:
    #             continue
    #         res.append(self.resources[i] <= __value.resources[i])
    #     return any(res) if len(res) else False
        
    # def __lt__(self, __value:object) -> bool:
    #     res = []
    #     for i in range(len(self.resources)):
    #         if self.resources[i] == __value.resources[i]:
    #             continue
    #         res.append(self.resources[i] < __value.resources[i])
    #     return any(res) if len(res) else False
    
    # def __ge__(self, __value:object) -> bool:
    #     res = []
    #     for i in range(len(self.resources)):
    #         if self.resources[i] == __value.resources[i]:
    #             continue
    #         res.append(self.resources[i] >= __value.resources[i])
    #     return all(res) if len(res) else True
    
    # def __gt__(self, __value:object) -> bool:
    #     res = []
    #     for i in range(len(self.resources)):
    #         if self.resources[i] == __value.resources[i]:
    #             continue
    #         res.append(self.resources[i] > __value.resources[i])
    #     return all(res) if len(res) else True
    
    def __getitem__(self, index:int | str) -> np.float32:
        if (type(index) == str):
            match index:
                case "cpu":
                    index = 0
                case "memory":
                    index = 1
                case "storage":
                    index = 2
                case _:
                    raise Exception("Not implemented.")
        return self.resources[index]
            
ZERO_NODE_RESOURCE = NodeResource()

class LinkResource:   
    @property
    def bandwidth(self) -> np.float32:
        return self.resources[0]
    def __init__(self, bandwidth:np.float32=None):
        bandwidth = 0 if bandwidth is None else bandwidth
        self.resources=np.array([bandwidth])
        
    @classmethod
    def fromArray(arr:np.ndarray):
        t = LinkResource()
        t.resources = arr
        return t
        
    def __copy__(self):
        clone = LinkResource()
        clone.resources = self.resources
        return clone
    
    def __deepcopy__(self, memo):
        clone = LinkResource()
        clone.resources = self.resources
        return clone
        
    def __len__(self) -> int:
        return len(self.resources)
        
    def __repr__(self) -> str:
        s = f"LinkResources(bandwidth={self.bandwidth})"
        return s
    
    def __reduce__(self) -> tuple[object, tuple[np.float32]]:
        return (self.__class__, (self.bandwidth,))
    
    def __add__(self, __value: object):
        c = LinkResource()
        c.resources = self.resources + __value.resources
        return c
    
    def __add__(self, __value: int):
        c = LinkResource()
        c.resources = self.resources + __value
        return c
    
    def __radd__(self, __value: int):
        c = LinkResource()
        c.resources = self.resources + __value
        return c
    
    def __sub__(self, __value: object):
        c = LinkResource()
        c.resources = self.resources - __value.resources
        return c
    
    def __sub__(self, __value: int):
        c = LinkResource()
        c.resources = self.resources - __value
        return c
    
    def __rsub__(self, __value: int):
        c = LinkResource()
        c.resources = __value - self.resources
        return c
    
    def __mul__(self, __value: int):
        c = LinkResource()
        c.resources = self.resources * __value
        return c
    
    def __mul__(self, __value: int):
        c = LinkResource()
        c.resources = self.resources * __value
        return c
    
    def __truediv__(self, __value: int):
        c = LinkResource()
        c.resources = self.resources / __value
        return c
    
    def __round__(self, ndigits: int=None):
        c = LinkResource()
        c.resources = np.round(self.resources, decimals=0 if ndigits is None else ndigits)
        return c
    
    def __eq__(self, __value: object) -> bool:
        if ((type(__value) == int) and (__value == 0)):
            return self.resources == __value
        return all(self.resources == __value.resources)
    
    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)
    
    def __le__(self, __value:object) -> bool:
        res = []
        for i in range(len(self.resources)):
            if self.resources[i] == __value.resources[i]:
                continue
            res.append(self.resources[i] <= __value.resources[i])
        return any(res) if len(res) else True
        
    def __lt__(self, __value:object) -> bool:
        res = []
        if ((type(__value) == int) and (__value == 0)):
            return any(self.resources < __value)
        for i in range(len(self.resources)):
            if self.resources[i] == __value.resources[i]:
                continue
            res.append(self.resources[i] < __value.resources[i])
        return any(res) if len(res) else True
    
    def __ge__(self, __value:object) -> bool:
        res = []
        for i in range(len(self.resources)):
            if self.resources[i] == __value.resources[i]:
                continue
            res.append(self.resources[i] >= __value.resources[i])
        return all(res) if len(res) else True
    
    def __gt__(self, __value:object) -> bool:
        res = []
        for i in range(len(self.resources)):
            if self.resources[i] == __value.resources[i]:
                continue
            res.append(self.resources[i] > __value.resources[i])
        return all(res) if len(res) else True
    
    def __getitem__(self, index:int | str) -> np.float32:
        if (type(index) == str):
            match index:
                case "bandwidth":
                    index = 0
                case _:
                    raise Exception("Not implemented.")
        return self.resources[index]
            
ZERO_LINK_RESOURCE = LinkResource()