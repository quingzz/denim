#ifndef MAIN_CPP_DISTRIBUTIONPARAMETRIC_H
#define MAIN_CPP_DISTRIBUTIONPARAMETRIC_H

#include "Transition.h"
#include <functional>

// Parent class for defined cdf distribution 
class TransitionParametricDist: public Transition {    
protected:
    std::vector<double> transitionProb;
    std::vector<double> probDist;
    void calcTransitionProb(std::function<double(double)> cdf_func);  
public:
    double getTransitionProb(size_t index) override;
    double getProbDist(size_t index) override;
    std::vector<double>& getTransitionProbRef() override;
};


#endif //MAIN_CPP_DISTRIBUTIONPARAMETRIC_H
