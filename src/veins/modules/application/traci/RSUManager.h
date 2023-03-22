#ifndef RSU_MANAGER_H
#define RSU_MANAGER_H

#include <map>
#include <string>
#include <iostream>
#include "omnetpp.h"
#include "veins/base/utils/SimpleAddress.h"
#include "Result.h"
#include "veins/base/utils/Coord.h"

namespace veins{
    class TraCIDemoRSU11p;
};
using namespace veins;

typedef struct
{
    double cpu;
    std::vector<double> mem;
    std::vector<simtime_t> wait;
    TraCIDemoRSU11p *rsu;
    std::string str()
    {
        std::stringstream ss;
        return ss.str();
    }
} RsuState;

class RSUManager
{
private:
    static std::map<LAddress::L2Type, RsuState *> rsus;
    static std::map<LAddress::L2Type, int> rsuMap;

public:
    static void release();
    static void registerRsu(TraCIDemoRSU11p *rsu);
    static void unregisterRsu(TraCIDemoRSU11p *rsu);
    static RsuState *getState(LAddress::L2Type addr);
    static Result<TraCIDemoRSU11p> getRsuInAera(Coord center, double radius);
};





#endif
