import multiprocessing as mp
import os
import uuid
import copy

from utilities.config import ConfigParser
from utilities.multiprocessing import MultiProcessing, IterToQueue
from utilities.dir import RecurseListDir, CleanDir
from FlexSliceMappingProblem import SliceMappingProblem, SaveProblem, LoadProblem
from FlexSliceMappingProblem.utilities import GraphClone

def Main(config:dict):
    print(config)
    PROBLEM_SETNAME = config["PROBLEM_SETNAME"]
    PROBLEM_COUNT = config["PROBLEM_COUNT"]
    OUTPUT_PATH = os.path.join("./data/problems", PROBLEM_SETNAME)
    CleanDir(OUTPUT_PATH)
    KEEPPHY = bool(config["KEEPPHY"])
    PHY_MODE = str(config["PHY"]["MODE"]).split("@")
    SFC_MODE = str(config["SFCSET"]["MODE"]).split("@")
    
    PHY_NODECAP = (config["PHY"]["NODE"]["CPU"],config["PHY"]["NODE"]["MEM"],config["PHY"]["NODE"]["STO"])
    PHY_LINKCAP = (config["PHY"]["LINK"]["BW"],)
    match PHY_MODE[0]:
        case "FROMGML":
            from FlexSliceMappingProblem.phy.fromgml import FromGmlGraphGenerator as PhyGraphGenerator
            phygraphGenerator = PhyGraphGenerator(gml_path=PHY_MODE[1], nodecap=PHY_NODECAP, linkcap=PHY_LINKCAP)
        case "FATTREE":
            from FlexSliceMappingProblem.phy.kfat import FatTreeGraphGenerator as PhyGraphGenerator
            phygraphGenerator = PhyGraphGenerator(
                k = int(PHY_MODE[1]),
                host_nodecap=(value["host"] for value in PHY_NODECAP),
                edge_nodecap=(value["edge"] for value in PHY_NODECAP),
                aggr_nodecap=(value["aggr"] for value in PHY_NODECAP),
                core_nodecap=(value["core"] for value in PHY_NODECAP),
                hostedge_linkcap=(value["hostedge"] for value in PHY_LINKCAP),
                edgeaggr_linkcap=(value["edgeaggr"] for value in PHY_LINKCAP),
                aggrcore_linkcap=(value["aggrcore"] for value in PHY_LINKCAP),
            )
        case _:
            raise Exception(f"[Invalid config] PHY/MODE={PHY_MODE[0]}")
        
    match SFC_MODE[0]:
        case "flex":
            from FlexSliceMappingProblem.slice.flex import FlexSliceGenerator as SliceGenerator
            sfcgraphGenerator = SliceGenerator(SFC_MODE[1], SFC_MODE[2], SFC_MODE[3])
        case _:
            raise Exception(f"[Invalid config] SFCSET/MODE={SFC_MODE[0]}")
    
    PHY = phygraphGenerator.Generate()
    for i in range(PROBLEM_COUNT):
        if not KEEPPHY:
            PHY = phygraphGenerator.Generate()
        SFC = sfcgraphGenerator.Generate()
        SFC_SET = []
        for i in range(config["SFCSET"]["SFCCOUNT"]):
            if not config["SFCSET"]["KEEPSFC"]:
                SFC = sfcgraphGenerator.Generate()
            else:
                SFC = GraphClone(SFC)
            SFC_SET.append(SFC)
        problem = SliceMappingProblem(phy=PHY, slices_set=SFC_SET)
        savepath = os.path.join(OUTPUT_PATH, f"{problem.name}.pkl.gz")
        SaveProblem(path=savepath, problem=problem)

def MpWorker(queue: mp.Queue):
    while queue.qsize():
        item = queue.get()
        Main(item)
    exit()

if __name__=="__main__":
    config_list = ConfigParser("./configs/ProblemSettings/dummy.yaml")
    q = IterToQueue(config_list)
    MultiProcessing(MpWorker, (q,), 1)
