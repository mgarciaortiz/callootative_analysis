from data_plotter import plotFitDataForCountry, plotRealData
from data_loader import load_data, clean_data, readDataForCountry
from data_sir import solveSIRModel


def plotFitData(countries, csvFile, fileFormat, dataType, plot, nprev, ndiscard, verbose):
    for countryName in countries:
        plotFitDataForCountry(countryName, csvFile, fileFormat, dataType, plot, nprev, ndiscard, verbose)


def plotSIRModelForData(countries, csvFile, initVal):
    data = load_data(csvFile)
    cases, useless  = clean_data(data, cumsum=True)
    for country in countries:
        casesCountry = readDataForCountry(cases, country)
        solveSIRModel(country, casesCountry, initVal)


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
       make_option("-w", "--dataType", type="string", dest="dataType", default="cases", help="cases or deaths"),
       make_option("-l", "--fit", action="store_true", dest="fit", default=False, help="Logistic regression"),
       make_option("-s", "--sir", action="store_true", dest="sir", default=False, help="SIR model"),
       make_option("-i", "--init", type="string", dest="init", default="90000,2,0", help="Initial values for S0, I0, R0 to solve SIR"),
                  ]
    parser          = OptionParser(option_list=option_list)
    (options, args) = parser.parse_args()
    countries = options.country
    if options.country:
        countries = options.country.split(",")
    else:
        countries = ["France", "Italy", "Spain", "Germany", "Portugal", "United_States_of_America", "United_Kingdom", "China", "Japan", "South_Korea", "Iran"]

    if options.real:
        plotRealData(countries, options.csvFile, options.format, options.ndiscard, options.dataType)
    elif options.fit:
        plotFitData(countries, options.csvFile, options.format, options.dataType, options.plot, options.nprev, options.ndiscard, options.verbose)
    elif options.sir:
        initialValues = [eval(v) for v in options.init.split(",")]
        plotSIRModelForData(countries, options.csvFile, initialValues)
    else:
        raise ValueError("Choose something to do!!!")
