from amazon.api import AmazonAPI
from ebaysdk.finding import Connection as finding
from ebaysdk.exception import ConnectionError
import csv
from fuzzywuzzy import fuzz

#keys
AWSkey = 'your AWS key here'
AWSSecretKey = 'your AWS secret key here'
amazonProductAdvName = 'your amazon product advertising name here'
EbayKey = 'your ebay developer key here'

search = u'put what you are looking for here EX: Taylormade golf club'

amazon = AmazonAPI(AWSkey,AWSSecretKey,amazonProductAdvName,MaxQPS=.9)
ebayApi = finding(appid=EbayKey, config_file=None)

path = open("AmazonEbayData.csv", "wt")
filewriter = csv.writer(path)
allData = []
filewriter.writerow(['Ebay Item Title', 'Ebay Item ID','Ebay Price','ebay Item URL', 'Amazon Item Title','Amazon ISBN', 'Amazon Price', 'Amazon Item URL', 'Price Difference'])

def findOnAmazon(ebayItem,ebayPrice,ebayItemID,ebayItemURL):
   response = amazon.search_n(1,Keywords=ebayItem, SearchIndex='All')
   amazonPrice = response[0].price_and_currency[0]
   amazonTitle = response[0].title
   amazonISBN = response[0].isbn
   amazonOfferURL = response[0].offer_url

    #check how close the titles are so we can better understand if they are the same product
   r = fuzz.partial_ratio(ebayItem,amazonTitle)

   if r > 75:
    # we can assume that they are the same thing
        if float(amazonPrice) > float(ebayPrice)*1.5:
            # check if the item is at least 50% more expensive on amazon so we have room to make money
            possibleReturn = float(amazonPrice) - float(ebayPrice)
            possret = float("{0:.2f}".format(possibleReturn))
            print(possret)
            data = [ebayItem,ebayItemID,ebayPrice,ebayItemURL,amazonTitle,amazonISBN,amazonPrice,amazonOfferURL,possret]
            allData.append(data)

def run():

    try:
        api_request = {
            'keywords': search,
            'itemFilter': [
                {'name': 'LocatedIn',
                 'value': 'US'},
                {'name': 'MinPrice',
                 'value': '0'},
                {'name': 'MaxPrice',
                 'value': '50.00'},

            ],
            'sortOrder': 'BestMatch',
        }

        response = ebayApi.execute('findItemsAdvanced', api_request)

        dict = response.reply.get('searchResult')
        clearedArray = dict.get('item')
        for item in clearedArray:

            ebaytitle = item.get('title')

            ebayItemID = item.get('itemId')
            ebayprice = item.get('sellingStatus')
            current = ebayprice.get('currentPrice')
            value = current.get('value')
            ebayURL = item.get('viewItemURL')
            try:
                findOnAmazon(ebaytitle,value,ebayItemID,ebayURL)
            except:
                print("couldn`t find matching object")

        for row in allData:
            filewriter.writerow(row)
        path.close()

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


if __name__ == '__main__':
    run()