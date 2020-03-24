# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
from scipy.optimize import minimize
from scipy.integrate import solve_ivp


def extendDateIndex(index, newSize):
    s="01/01/2020"
    date = datetime.strptime(s, '%d/%m/%Y')
    values = list(map(lambda x: (pd.to_datetime(x) - date).days, index))
    newValues = [date + timedelta(days=int(i)) for i in values]
    current = date + timedelta(days=int(values[-1])) # datetime.strptime(index.tail(1), '%d/%m/%y')

    while len(newValues) < newSize:
        current = current + timedelta(days=1)
        newValues = np.append(newValues,  current)
    newValues = [datetime.strftime(i, '%d/%m/%y') for i in newValues]

    return newValues


def solveSIRWithFittedParameters(beta, gamma, data, initVal):
    """
    Predicts the distributions for the susceptibles, infected and
    recovered persons over 100 days, given the fitted beta and gamma
    parameters up to the present day.
    """
    predictRange = 100
    newIndex = extendDateIndex(data.index, predictRange)
    size = len(newIndex)
    #     [-beta*S*I, beta*S*I-gamma*I, gamma*I]
    #     S = y[0]     I = y[1]     R = y[2]
    SIR = lambda t, y: [-beta*y[0]*y[1], beta*y[0]*y[1]-gamma*y[1], gamma*y[1]]
    extendedActual = np.concatenate((data.values, [None] * (size - len(data.values))))

    return newIndex, extendedActual, solve_ivp(SIR, [0, size], initVal, t_eval=np.arange(0, size, 1))


def functionalToMinimise(point, data, initVal):
    """
    Returns the RMS between confirmed cases and the estimated infected
    persons with given beta and gamma.
    """
    data = data.values
    size = len(data)
    beta, gamma = point
    #     [-beta*S*I, beta*S*I-gamma*I, gamma*I]
    #     S = y[0]     I = y[1]     R = y[2]
    SIR = lambda t, y: [-beta*y[0]*y[1], beta*y[0]*y[1]-gamma*y[1], gamma*y[1]]
    solution = solve_ivp(SIR, [0, size], initVal, t_eval=np.arange(0, size, 1), vectorized=True)
    return np.sqrt(np.mean((solution.y[1] - data)**2))


def solveSIRModel(country, data, initVal):
    """
    Runs the optimisation to estimate the beta and gamma fitting the
    given cases, and get predicted distributions.
    """
    data = data[data > 10]
    # data = data.iloc[0:]
    optimal = minimize(functionalToMinimise,
                       [0.0001, 0.0001],
                       args=(data, initVal),
                       method='L-BFGS-B',
                       bounds=[(1.e-8, 0.4), (1.e-8, 0.4)]
                       )
    print(optimal)
    beta, gamma = optimal.x
    print(f"country = {country},\n beta = {beta:.8f},\n gamma = {gamma:.8f},\n r_0 = {(beta/gamma):.8f}")
    newIndex, extendedActual, prediction = solveSIRWithFittedParameters(beta, gamma, data, initVal)
    df = pd.DataFrame({'Experimental': extendedActual,
                       'Susceptibles': prediction.y[0],
                       'Infected': prediction.y[1],
                       'Recovered': prediction.y[2]
                       },
                      index=newIndex,
                      )
    fig, ax = plt.subplots(figsize=(15, 15))
    plt.rc('font', size=14)
    ax.set_title(country)

    # from matplotlib.dates import DateFormatter
    # import matplotlib.dates as mdates
    # date_form = DateFormatter("%d/%m/%Y")
    # ax.xaxis.set_major_formatter(date_form)
    # ax.xaxis.set_minor_formatter(date_form)

    # # Ensure a major tick for each week using (interval=1)
    # ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    # ax.xaxis.set_minor_locator(mdates.DayLocator(interval=2))

    # plt.xticks(range(len(newIndex)), newIndex, rotation=90)
    ax.xaxis.set_major_locator(plt.MaxNLocator(extendedActual.size//3))
    df.plot(ax=ax)
    plt.xticks(rotation=90)
    plt.grid()
    # fig.savefig(f"{country}.png")
    plt.show()
