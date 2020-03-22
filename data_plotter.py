import matplotlib.pyplot as plt
from data_fit import  logisticFunction, exponentFunction, computeLogisticFitForCountry
from data_loader import getXYDataForCountry

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


def plotFitDataForCountry(countryName, fileName, fileFormat, plot, nprev, ndiscard, verbose):
    x, y = getXYDataForCountry(countryName, fileName, fileFormat, ndiscard)
    fit, sol, errors, expFit = computeLogisticFitForCountry(countryName, x, y, verbose)

    if plot:
        plt = preparePlot(x, y, sol, fit, errors, expFit)
        plt.title("{}".format(countryName))
        if nprev:
            for nd in range(1, nprev + 1):
                fit, sol, errors, expFit = computeLogisticFitForCountry(countryName, x[:-nd], y[:-nd], verbose=1)
                if fit:
                    pred_x = list(range(max(x), sol))
                    label = "Logistic {} days ago".format(nd)
                    plt.plot(x + pred_x, [logisticFunction(i, fit[0][0], fit[0][1], fit[0][2]) for i in x + pred_x],
                             label=label)
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