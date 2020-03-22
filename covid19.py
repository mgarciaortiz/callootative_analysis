from data_plotter import plotFitDataForCountry, plotRealData
from data_loader import load_data

def plotFitData(countries, csvFile, fileFormat, plot, nprev, ndiscard, verbose):
    for countryName in countries:
        plotFitDataForCountry(countryName, csvFile, fileFormat, plot, nprev, ndiscard, verbose)


data = load_data('covid19-20200320.csv')


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

    data = load_data(options.csvFile)

    countries = options.country
    if options.country:
        countries = options.country.split(",")
    else:
        countries = ["France", "Italy", "Spain", "Germany", "Portugal", "United_States", "United_Kingdom", "China", "Japan", "South_Korea", "Iran"]

    if options.real:
        plotRealData(countries, options.csvFile, options.format)
    else:
        plotFitData(countries, options.csvFile, options.format, options.plot, options.nprev, options.ndiscard, options.verbose)
