from datetime import datetime, timedelta
import pandas as pd
import os

FMT = '%d/%m/%Y'

def load_data(fileName):


    # Open file inependently of where your project is located
    __location__ = os.path.realpath( os.path.join(os.getcwd(), os.path.dirname(__file__)))
    fileName = os.path.join(__location__, fileName)
    df = pd.read_csv(fileName, engine="python")

    return df



def clean_data(df, cumsum = False):

    # Create a new dataframe with all dates
    dates = df['DateRep'].map(lambda x: (datetime.strptime(x, FMT)))
    date_min = min(dates)
    date_max = max(dates)
    data_cases = pd.DataFrame(index=pd.date_range(date_min, date_max))
    data_deaths = pd.DataFrame(index=pd.date_range(date_min, date_max))

    # fill the dataframe with data from each country
    countries = set(df['Country'])
    for country in countries:
        df_country = df[df['Country'] == country]
        df_country.index = df_country['DateRep'].map(lambda x: (datetime.strptime(x, FMT)))

        data_cases = data_cases.join(df_country['Cases'], how='outer')
        data_cases.rename(columns={'Cases': country}, inplace=True)

        data_deaths = data_deaths.join(df_country['Deaths'], how='outer')
        data_deaths.rename(columns={'Deaths': country}, inplace=True)

    data_deaths = data_deaths.drop_duplicates().fillna(0)
    data_cases = data_cases.drop_duplicates().fillna(0)

    if cumsum:
        data_deaths = data_deaths.cumsum()
        data_cases = data_cases.cumsum()

    return data_cases, data_deaths



def toDate(delta):
    s="2020-01-01 00:00:00"
    date = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    date += timedelta(days=delta)
    return date


def getDataFrame(fileName):
    return pd.read_csv(fileName)


def readDataForCountry(df, country):
    df = df['%s' % country]
    # print(df)
    if df.empty:
        raise ValueError(">>>>> readDataForCountry: Problem with reading data for %s!" % country)

    return df


def readDataForCountryFormatTwo(country, fileName="new_cases.csv"):
    df = pd.read_csv(fileName)
    FMT = '%Y-%m-%d'
    try:
        df = df.loc[:, ['date', '{}'.format(country)]]
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


def getXYDataForCountry(countryName, fileName, fileFormat, ndiscard, dataType):
    data = load_data(fileName)
    cases, deaths = clean_data(data, cumsum=True)
    if dataType == 'Cases':
        df = cases
    elif dataType == 'Deaths':
        df = deaths
    else:
        raise ValueError("Unknown data type")

    if fileFormat == 1:
        df = readDataForCountry(df, countryName)
        lastDate = df.index[-1]
    elif fileFormat == 2:
        df = readDataForCountryFormatTwo(countryName, fileName)
        dateName = 'date'
        lastDate = toDate(int(df[dateName].iloc[-1]))
    else:
        raise ValueError(">>>>> getXYDataForCountry: Unknown file format!")

    x = df.index[ndiscard:]
    y = df.values[ndiscard:]

    return x, y
