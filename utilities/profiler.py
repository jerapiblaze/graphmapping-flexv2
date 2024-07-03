import time

class StopWatch:
    def __init__(self, name:str, msg:bool=False):
        self.name = name
        self.stops = []
        self.last_stop = None
        self.tbegin = None
        self.tend = None
        self.msg = msg
    
    def start(self):
        self.tbegin = time.perf_counter()
        self.last_stop = time.perf_counter()
        line = f"START\n"
        self.stops.append(line)
        if self.msg:
            print(line)

    def end(self) -> int:
        if not self.tend:
            self.tend = time.perf_counter()
        return self.total_time()

    def total_time(self) -> int:
        gap = self.tend - self.tbegin
        return gap

    def add_stop(self, message:str):
        current_time = time.perf_counter()
        gap_time = current_time - self.last_stop
        self.last_stop = current_time
        line = f"{self.last_stop} [{self.name}] {message} ({gap_time})\n"
        self.stops.append(line)
        if self.msg:
            print(line)

    def write_to_file(self, filepath:str, mode:str="at"):
        if not filepath:
            return
        with open(filepath, mode=mode) as f:
            f.writelines(self.stops)
