#include "CarManager.h"
#include "TraCIDemo11p.h"

std::map<long, TraCIDemo11p *> CarManager::cars;

void CarManager::registerCar(TraCIDemo11p *car)
{
    auto it = cars.find(car->getCarId());
    if (it == cars.end()) {
        cars[car->getCarId()] = car;
        std::cout << car->getCarId() << " register, now has " << cars.size() << std::endl;
    }
}

void CarManager::unRegisterCar(TraCIDemo11p *car)
{
    auto it = cars.find(car->getCarId());
    if (it != cars.end())
    {
        cars.erase(it);
    }
}

Coord CarManager::getPosition(long id)
{
    auto it = cars.find(id);
    if (it != cars.end())
    {
        return it->second->getCurPosition();
    }
    return Coord(-1, -1);
}

Result<TraCIDemo11p> CarManager::getCarInAera(Coord center, double radius)
{
    Result<TraCIDemo11p> result;
    for (auto &it : cars)
    {
        double distance = center.distance(it.second->getCurPosition());
        if (center.distance(it.second->getCurPosition()) < radius)
        {
            result.push(it.second);
        }
    }
    result.reset();
    return result;
}
