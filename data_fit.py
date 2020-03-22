import numpy as np
from scipy.optimize import curve_fit
from scipy.optimize import fsolve
from data_loader import toDate

def logisticFunction(t, a, b, c):
    # a =  infection speed
    # b = day with the max infect
    # c = total number of recorded infected people at saturation
    return c/(1+np.exp(-(t-b)/a))

def exponentFunction(t, a, b, c):
    return a*np.exp(b*(t-c))

def gaussianFunction(x, a, x0, sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))


def computeLogisticFitForCountry(countryName, x, y, verbose):
    try:
        fit = curve_fit(logisticFunction, x, y, p0=[2, 10, 200000])
        params, covmat = fit
        a, b, c = params
        errors = [np.sqrt(fit[1][i][i]) for i in [0, 1, 2]]
        sol = int(fsolve(lambda t: logisticFunction(t, a, b, c) - int(c), b))
        predDate = toDate(sol)
    except RuntimeError:
        print(">>>>>> Could not compute logistic fit for {}".format(countryName))
        fit = None
        sol = None
        errors = None

    try:
        expFit = curve_fit(exponentFunction, x, y, p0=[1, 1, 10])
    except RuntimeError:
        print(">>>>>> Could not compute exponential fit for {}".format(countryName))
        expFit = None

    if fit and verbose:
        print("*******************************************")
        print("Country                     = ", countryName)
        print("Last available date         = ", toDate(x[-1]))
        print("Logisitic Fit               = ", fit)
        print("Log. Errors                 = ", errors)
        print("Number of days from 1st Jan = ", sol)
        print("Predicted date for inflection = ", toDate(np.ceil(b)))
        print("Predicted date for saturation = ", predDate)
        print("*******************************************")

    return fit, sol, errors, expFit

