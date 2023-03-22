#ifndef RESULT_H
#define RESULT_H

#include <vector>

template <typename T>
class Result
{
private:
    std::vector<T *> result;
    typename std::vector<T *>::iterator s_it;

public:
    Result()
    {
        s_it = result.begin();
    }

    void push(T *item)
    {
        this->result.push_back(item);
    }

    void reset()
    {
        s_it = result.begin();
    }

    bool hasNext()
    {
        return s_it != result.end();
    }

    T *next()
    {
        T *n = *s_it;
        s_it++;
        return n;
    }

    size_t size() {
        return result.size();
    }
};

#endif