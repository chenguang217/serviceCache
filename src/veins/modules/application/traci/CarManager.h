#ifndef CAR_MANAGER_H
#define CAR_MANAGER_H

#include <map>
#include <vector>
#include "veins/base/utils/Coord.h"
#include "Result.h"

namespace veins {
    class TraCIDemo11p;
};
using namespace veins;


class CarManager
{
private:
    static std::map<long, TraCIDemo11p *> cars;

public:
    
    static void registerCar(TraCIDemo11p *);
    static void unRegisterCar(TraCIDemo11p *);
    static Coord getPosition(long);
    static Result<TraCIDemo11p> getCarInAera(Coord center, double radius);
};

#endif
