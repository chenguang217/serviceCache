#include "RSUManager.h"
#include "TraCIDemoRSU11p.h"

std::map<LAddress::L2Type, RsuState *> RSUManager::rsus;
std::map<LAddress::L2Type, int> RSUManager::rsuMap;



void RSUManager::release()
{
    for (auto it = RSUManager::rsus.begin(); it != RSUManager::rsus.end();)
    {
        delete it->second;
        RSUManager::rsus.erase(it++);
    }
}

void RSUManager::registerRsu(veins::TraCIDemoRSU11p *rsu)
{
    RsuState *state = new RsuState();
    state->rsu = rsu;
    rsus[rsu->getRSUId()] = state;
    rsuMap[rsu->getRSUId()] = rsu->getNode()->getIndex();
    std::cout << rsu->getRSUId() << " register, now has " << rsus.size() << " rsus" << std::endl;
}

void RSUManager::unregisterRsu(TraCIDemoRSU11p *rsu)
{
    auto it = rsus.find(rsu->getRSUId());
    if (it != rsus.end()) {
        delete it->second;
        rsus.erase(it);
    }
}

RsuState *RSUManager::getState(LAddress::L2Type addr)
{
    auto it = rsus.find(addr);
    if (it != rsus.end())
    {
        return it->second;
    }
    return nullptr;
}

Result<TraCIDemoRSU11p> RSUManager::getRsuInAera(Coord center, double radius)
{
    Result<TraCIDemoRSU11p> result;
    for (auto &it : rsus)
    {
        if (center.distance(it.second->rsu->getCurPosition()) < radius)
        {
            result.push(it.second->rsu);
        }
    }
    result.reset();
    return result;
}
