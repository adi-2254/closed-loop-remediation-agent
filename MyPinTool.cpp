#include "pin.H"
#include <iostream>
#include <fstream>
#include <map>
#include <string>
#include <vector>
#include <algorithm>
#include <iomanip>

KNOB<std::string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool", "o", "profiler_trace.out", "Output file for the flat profile trace");
std::ofstream TraceFile;

struct RoutineProfile {
    std::string name;
    UINT64 totalInstructions;
};

std::map<ADDRINT, RoutineProfile> routineMap;

VOID CountBblInstructions(ADDRINT rtnAddr, UINT32 numInst) {
    routineMap[rtnAddr].totalInstructions += numInst;
}

VOID Trace(TRACE trace, VOID *v) {
    RTN rtn = TRACE_Rtn(trace);
    if (!RTN_Valid(rtn)) return; 

    ADDRINT rtnAddr = RTN_Address(rtn);
    std::string rtnName = RTN_Name(rtn);

    if (routineMap.find(rtnAddr) == routineMap.end()) {
        routineMap[rtnAddr].name = rtnName;
        routineMap[rtnAddr].totalInstructions = 0;
    }

    for (BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl)) {
        BBL_InsertCall(bbl, IPOINT_ANYWHERE, (AFUNPTR)CountBblInstructions,
                       IARG_ADDRINT, rtnAddr,          
                       IARG_UINT32, BBL_NumIns(bbl),   
                       IARG_END);
    }
}

VOID Fini(INT32 code, VOID *v) {
    std::vector<RoutineProfile> profiles;
    for (auto const& [addr, prof] : routineMap) {
        if (prof.totalInstructions > 0) { 
            profiles.push_back(prof);
        }
    }

    std::sort(profiles.begin(), profiles.end(), [](const RoutineProfile& a, const RoutineProfile& b) {
        return a.totalInstructions > b.totalInstructions;
    });

    TraceFile << "=========================================================\n";
    TraceFile << "FLAT PERFORMANCE ANALYSIS REPORT\n";
    TraceFile << "=========================================================\n";
    TraceFile << std::left << std::setw(15) << "Instructions" 
              << std::left << std::setw(10) << "% Total" 
              << "Function Name\n";
    TraceFile << "---------------------------------------------------------\n";

    UINT64 totalAppInstructions = 0;
    for (const auto& prof : profiles) totalAppInstructions += prof.totalInstructions;

    for (const auto& prof : profiles) {
        double percentage = (static_cast<double>(prof.totalInstructions) / totalAppInstructions) * 100.0;
        TraceFile << std::left << std::setw(15) << prof.totalInstructions
                  << std::fixed << std::setprecision(2) << std::left << std::setw(9) << percentage << "% "
                  << prof.name << "\n";
    }

    TraceFile << "=========================================================\n";
    TraceFile.close();
}

int main(int argc, char *argv[]) {
    PIN_InitSymbols();
    if (PIN_Init(argc, argv)) {
        std::cerr << "Initialization failed." << std::endl;
        return -1;
    }

    TraceFile.open(KnobOutputFile.Value().c_str());
    TRACE_AddInstrumentFunction(Trace, 0);
    PIN_AddFiniFunction(Fini, 0);
    PIN_StartProgram();
    return 0;
}