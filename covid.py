# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error
from scipy.optimize import curve_fit
from scipy.optimize import fsolve

def logisticFunction(t, a, b, c):
    # a =  infection speed
    # b = day with the max infect
    # c = total number of recorded infected people at saturation
    return c/(1+np.exp(-(t-b)/a))


def exponentFunction(t, a, b, c):
    return a*np.exp(b*(t-c))


def toDate(delta):
    s="2020-01-01 00:00:00"
    date = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    date += timedelta(days=delta)
    return date


def preparePlot(x, y, sol, logisticFit, errors, expFit=None):
    plt.rcParams['figure.figsize'] = [10, 10]
    plt.rc('font', size=14)
    plt.scatter(x, y, label="Experimental data",color="red")
    if sol:
        pred_x = list(range(max(x), sol))
    else:
        pred_x = list(range(max(x), max(x) + 10))
    if logisticFit:
        params, covmat = logisticFit
        a, b, c = params
        yfitReal = [logisticFunction(i, logisticFit[0][0], logisticFit[0][1], logisticFit[0][2]) for i in x]
        yfitExtrap = [logisticFunction(i, logisticFit[0][0], logisticFit[0][1], logisticFit[0][2]) for i in pred_x]
        plt.plot(x + pred_x, yfitReal + yfitExtrap, label="Logistic" )
        nSigma = 3
        if np.isfinite(errors[2]) and errors[2] < 0.5 * c:
            err = nSigma * errors[2]
            plt.ylim((min(y)*0.9, max(yfitExtrap + err)*1.1))
            plt.fill_between(pred_x, yfitExtrap - err, yfitExtrap + err, alpha=1, edgecolor='#3F7F4C', facecolor='#7EFF99', linewidth=0)
        else:
            plt.ylim((min(y)*0.9, c*1.1))
    if expFit:
        plt.plot(x + pred_x, [exponentFunction(i, expFit[0][0], expFit[0][1], expFit[0][2]) for i in x + pred_x], label="Exponential" )
    plt.legend()
    plt.xlabel("Days since 1st January 2020")
    plt.ylabel("Number of infected persons")
    plt.grid()
    # plt.show()
    return plt


def getDataFrame(fileName):
    return pd.read_csv(fileName)


def readDataForCountry(country, fileName):
    df = pd.read_csv(fileName)
    df = df[df.Country.str.match('%s' % country, case=False)]
    # if country == "EU":
    #     df = df[df.EU.str.match('EU', case=False)]
    #     print(df)
    #     exit()
    # print(df)
    FMT = '%d/%m/%Y'
    df = df.loc[:,['DateRep','Cases']]
    df = df[::-1]
    date = df['DateRep']
    df['DateRep'] = date.map(lambda x: (datetime.strptime(x, FMT) - datetime.strptime("01/01/2020", FMT)).days)
    new_cases = df['Cases']
    df['Cases'] = new_cases.cumsum(axis=0)
    # print(df)
    if df.empty:
        raise ValueError(">>>>> readDataForCountry: Problem with reading data for %s!" % country)

    return df


def readDataForCountryFormatTwo(country, fileName="new_cases.csv"):
    df = pd.read_csv(fileName)
    FMT = '%Y-%m-%d'
    try:
        df = df.loc[:,['date','{}'.format(country)]]
    except:
        raise KeyError(">>>>> readDataForCountryFormatTwo: Country {} not available.".format(country))
    date = df['date']
    df['date'] = date.map(lambda x: (datetime.strptime(x, FMT) - datetime.strptime("2020-01-01", FMT)).days)
    df = df.dropna()
    new_cases = df['{}'.format(country)]
    df['{}'.format(country)] = new_cases.cumsum(axis=0)
    # print(df)
    if df.empty:
        raise ValueError(">>>>> readDataForCountryFormatTwo: Problem with reading data for %s!" % country)

    return df


def getXYDataForCountry(countryName, fileName, fileFormat, ndiscard):
    if fileFormat == 1:
        df = readDataForCountry(countryName, fileName)
        dateName = 'DateRep'
        lastDate = toDate(int(df[dateName].iloc[-1]))
    elif fileFormat == 2:
        df = readDataForCountryFormatTwo(countryName, fileName)
        dateName = 'date'
        lastDate = toDate(int(df[dateName].iloc[-1]))
    else:
        raise ValueError(">>>>> getXYDataForCountry: Unknown file format!")

    x = list(df.iloc[ndiscard:,0])
    y = list(df.iloc[ndiscard:,1])
    
    return x, y


def computeLogisticFitForCountry(countryName, x, y,  verbose):
    try:
        fit = curve_fit(logisticFunction, x, y, p0=[2,10,200000])
        params, covmat = fit
        a, b, c = params
        errors = [np.sqrt(fit[1][i][i]) for i in [0,1,2]]
        sol = int( fsolve(lambda t: logisticFunction(t, a, b, c) - int(c), b) )
        predDate = toDate(sol)
    except RuntimeError:
        print(">>>>>> Could not compute logistic fit for {}".format(countryName))
        fit = None
        sol = None
        errors = None

    try:
        expFit = curve_fit(exponentFunction, x, y, p0=[1,1,10])
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


def plotDataForCountry(countryName, fileName, fileFormat, plot, nprev, ndiscard, verbose):
    x, y = getXYDataForCountry(countryName, fileName, fileFormat, ndiscard)
    fit, sol, errors, expFit = computeLogisticFitForCountry(countryName, x, y, verbose)

    if plot:
        plt = preparePlot(x, y, sol, fit, errors, expFit)
        plt.title("{}".format(countryName))
        if nprev:
            for nd in range(1, nprev+1):
                fit, sol, errors, expFit = computeLogisticFitForCountry(countryName, x[:-nd], y[:-nd], verbose=1)
                if fit:
                    pred_x = list(range(max(x), sol))
                    label = "Logistic {} days ago".format(nd)
                    plt.plot(x + pred_x, [logisticFunction(i, fit[0][0], fit[0][1], fit[0][2]) for i in x + pred_x], label=label)
                    plt.legend()
                
        plt.show()

        
def plotRealData(countries, csvFile, fileFormat):
    for countryName in countries:
        x, y = getXYDataForCountry(countryName, csvFile, fileFormat)
        plt.rcParams['figure.figsize'] = [10, 10]
        plt.rc('font', size=14)
        plt.plot(x, y, linewidth=3, label="{}".format(countryName))
    plt.legend()
    plt.xlabel("Days since 1st January 2020")
    plt.ylabel("Number of infected persons")
    plt.grid()
    plt.show()


def main(countries, csvFile, fileFormat, plot, nprev, ndiscard, verbose):
    for countryName in countries:
        plotDataForCountry(countryName, csvFile, fileFormat, plot, nprev, ndiscard, verbose)


if __name__ == "__main__":
    # Usage: python3 covid19.py -f covid19-20200317.csv -p
    # Usage: python3 covid19.py -f covid19-20200317.csv -p -c France,Italy
    from optparse import OptionParser, make_option
    option_list = [
       make_option("-f", "--csvFile", type="string", dest="csvFile", help="CSV file with data"),
       make_option("-t", "--format", type=int, dest="format", default=1, help="File format type 1 or 2"),
       make_option("-c", "--country", type="string", dest="country", default=None, help="Country name"),
       make_option("-v", "--verbose", type=int, dest="verbose", default=1, help="Output verbosity"),
       make_option("-p", "--plot", action="store_true", dest="plot", default=False, help="Plot data"),
       make_option("-r", "--real", action="store_true", dest="real", default=False, help="Plot real data"),
       make_option("-n", "--ndays", type=int, dest="nprev", default=0, help="Plot for last n days"),
       make_option("-d", "--ndiscard", type=int, dest="ndiscard", default=0, help="Discard first n days"),
                  ]
    parser          = OptionParser(option_list=option_list)
    (options, args) = parser.parse_args()
    countries = options.country
    if options.country:
        countries = options.country.split(",") 
    else:
        countries = ["France", "Italy", "Spain", "Germany", "Portugal", "United_States", "United_Kingdom", "China", "Japan", "South_Korea", "Iran"]
                
    if options.real:
        plotRealData(countries, options.csvFile, options.format)
    else:
        main(countries, options.csvFile, options.format, options.plot, options.nprev, options.ndiscard, options.verbose)
