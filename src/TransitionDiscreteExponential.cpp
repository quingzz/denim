//
// Created by thinh on 05/03/2021.
//

#include <iostream>
#include "TransitionDiscreteExponential.h"
#include "myProb.h"


TransitionDiscreteExponential::TransitionDiscreteExponential(double rate) {
    this->rate = rate;
    // call calcTransitionProb inherited from TransitionParametricDist 
    // pass exponential_cdf function with its parameter
    // https://people.sc.fsu.edu/~jburkardt/cpp_src/prob/prob.cpp
    calcTransitionProb([rate](double timestep){return exponential_cdf(timestep, 0, 1/rate);});
    this->distName = "exponential";
}


double TransitionDiscreteExponential::getRate() {
    return rate;
}