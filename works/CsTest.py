import os
import socket
import urllib2
from PyQt4.QtCore import QThread, pyqtSignal
from logs.LogManager import LogManager
from spiders.Spider import Spider
from utils.Csv import Csv
from utils.Regex import Regex
from utils.Utils import Utils

__author__ = 'Rabbi'


class CsTest(QThread):
    notifyProduct = pyqtSignal(object)

    def __init__(self):
        QThread.__init__(self)
        self.logger = LogManager(__name__)
        self.spider = Spider()
        self.regex = Regex()
        dupCsvReader = Csv()
        self.dupCsvRows0 = dupCsvReader.readCsvRow('cs_product.csv', 0)
        self.dupCsvRows = dupCsvReader.readCsvRow('cs_product.csv', 1)
        self.csvWriter = Csv('cs_product.csv')
        #        self.mainUrl = 'http://www.cs-catering-equipment.co.uk/'
        self.mainUrl = 'http://www.cs-catering-equipment.co.uk/brands'
        self.utils = Utils()
        if 'Product Code' not in self.dupCsvRows:
            self.csvWriter.writeCsvRow(
                ['URL', 'Product Code', 'Product Name', 'Manufacturer', 'List Price', 'Product Price', 'Discount',
                 'Product Short Description', 'Product Long Description', 'Product Technical Specifications', 'Warranty'
                    ,
                 'Delivery',
                 'Product Image',
                 'Category 1', 'Category 2', 'Category 3', 'Category 4', 'Brand Image'])
        self.totalProducts = len(self.dupCsvRows)

    def run(self):
        self.scrapBrands()
        self.notifyProduct.emit('<font color=red><b>Finished Scraping All Brands.</b></font>')

    def scrapBrands(self):
        self.notifyProduct.emit('<font color=green><b>Main URL: %s<b></font>' % self.mainUrl)
        self.notifyProduct.emit('<b>Try To scrap All Brands.<b>')
        data = self.spider.fetchData(self.mainUrl)
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            brandChunks = self.regex.getAllSearchedData('(?i)<div class="man-group man-group-[a-z]">(.*?)</div>', data)
            if brandChunks and len(brandChunks) > 0:
                for brandChunk in brandChunks:
                    brands = self.regex.getAllSearchedData('(?i)<a href="([^"]*)"[^>]*?>([^<]*)</a>', brandChunk)
                    self.notifyProduct.emit('<b>Total Brands Found: %s<b>' % str(len(brands)))
                    if brands and len(brands) > 0:
                        for brand in brands:
                            try:
                                self.scrapBrandInfo(brand[0], 'Shop By Brand', brand[1])
                            except Exception, x:
                                self.logger.error(x)

    def scrapBrandInfo(self, url, parentBrand, brand):
        self.notifyProduct.emit('<font color=green><b>Brand URL: %s<b></font>' % url)
        self.notifyProduct.emit('<b>Try to get info for brand: %s<b>' % brand)
        data = self.spider.fetchData(url)
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            #            desc = self.regex.getSearchedDataGroups(
            #                '(?i)<div class="category-head"> <h2>[^<]*</h2> </div> <img src="([^"]*)"[^>]*?>(.*?)<div', data)
            #            brandDesc = ''
            #            brandImage = ''
            #            if desc:
            #                brandDesc = desc.group(2)
            #                brandImage = self.regex.getSearchedData('(?i)/([a-zA-Z0-9-_.]*)$', desc.group(1))
            #                self.notifyBrand.emit('<b>Try to download image[%s]. Please wait... <b>' % brandImage)
            #                self.utils.downloadFile(desc.group(1), 'all_brand_image/' + brandImage)
            #            csvData = [url, parentBrand, brand, brandDesc, brandImage, '']
            #            print [url, parentBrand, brand, desc.group(2), brandImage, '']
            #            self.csvWriter.writeCsvRow(csvData)
            #            self.notifyBrand.emit('<font color=green><b>Brand Details: %s<b></font>' % str(csvData))

            subCat = self.regex.getSearchedData('(?i)<ul class="subcategory-listing">(.*?)</ul>', data)
            if subCat and len(subCat) > 0:
                subCatChunks = self.regex.getAllSearchedData('(?i)<a href="([^"]*)" title="([^"]*)">', subCat)
                if subCatChunks and len(subCatChunks) > 0:
                    for subCatChunk in subCatChunks:
                        try:
                        #                            self.scrapSubBrandInfo(subCatChunk[0], brand, subCatChunk[1])
                            self.scrapProductsDetails(subCatChunk[0])
                        except Exception, x:
                            self.logger.error(x)

    def scrapSubBrandInfo(self, url, parentBrand, brand):
        self.notifyProduct.emit('<font color=green><b>Brand URL: %s<b></font>' % url)
        self.notifyProduct.emit('<b>Try to get info for brand: %s<b>' % brand)
        data = self.spider.fetchData(url + '?limit=10000&mode=list')
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            #            brandImage = ''
            #            brandDesc = self.regex.getSearchedData('(?i)<div class="category-description std">([^<]*)</div>', data)
            #            brandImageUrl = self.regex.getSearchedData('(?i)<p class="category-image"><img src="([^"]*)"', data)
            #            if brandImageUrl and len(brandImageUrl) > 0:
            #                brandImage = self.regex.getSearchedData('(?i)/([a-zA-Z0-9-_.]*)$', brandImageUrl)
            #                self.notifyBrand.emit('<b>Try to download image[%s]. Please wait... <b>' % brandImage)
            #                self.utils.downloadFile(brandImageUrl, 'all_brand_image/' + brandImage)
            #
            #            productCodes = []
            products = self.regex.getAllSearchedData('(?i)<div class="listing-item[^"]*?">(.*?)</div>', data)
            if products and len(products) > 0:
                for product in products:
                    productDetailUrl = self.regex.getSearchedData('(?i)<a href="([^"]*)"', product)
                    print productDetailUrl
                #                    data = self.spider.fetchData(productDetailUrl)
                #                    if data and len(data) > 0:
                #                        data = self.regex.reduceNewLine(data)
                #                        data = self.regex.reduceBlankSpace(data)
                #                        productCode = self.regex.getSearchedData(
                #                            '(?i)<span class="manufacturer-box-label">Model No:</span>([^<]*)</p>', data)
                #                        if productCode and len(productCode.strip()) > 0:
                #                            productCodes.append(productCode)
                #            csvData = ['', parentBrand, brand, brandDesc, brandImage, ','.join(productCodes)]
                #            self.csvWriter.writeCsvRow(csvData)
                #            self.notifyBrand.emit('<font color=green><b>Brand Details: %s<b></font>' % str(csvData))

    def scrapProductsDetails(self, url):
        self.logger.debug('Product Details URL: ' + url)
#        self.notifyProduct.emit('<b>Try to scrap all products under Category[%s]</b>' % category4Name)
        self.notifyProduct.emit('<font color=green><b>Category URL: %s</b></font>' % url)
        maxLimit = 25
        maxLimitChunk = self.spider.fetchData(url + '?mode=list')
        if maxLimitChunk and len(maxLimitChunk):
            maxLimitChunk = self.regex.reduceNewLine(maxLimitChunk)
            maxLimitChunk = self.regex.reduceBlankSpace(maxLimitChunk)
            maxLimits = self.regex.getAllSearchedData('<option value="[^"]*limit=(\d+)[^"]*"', maxLimitChunk)
            #            print maxLimits
            if maxLimits and len(maxLimits) > 0:
                maxLimit = max(map(int, maxLimits))
                #                print maxLimit

                #        self.notifyProduct.emit('<font color=blue><b>Max Limit: %s</b></font>' % str(maxLimit))

        data = self.spider.fetchData(url + '?limit=' + str(maxLimit) + '&mode=list')
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            category1Name = category2Name = category3Name = ''
            categoryChunk = self.regex.getAllSearchedData('<li class="category\d+"> <a href="[^"]*?" title="([^"]*)"',
                data)
            if categoryChunk and len(categoryChunk) == 3:
                category1Name, category2Name, category3Name = categoryChunk[0].strip(), categoryChunk[1].strip(), categoryChunk[2].strip()
            elif categoryChunk and len(categoryChunk) == 2:
                category1Name, category2Name = categoryChunk[0].strip(), categoryChunk[1].strip()
            elif categoryChunk and len(categoryChunk) == 1:
                category1Name = categoryChunk[0].strip()

            category4Name = self.regex.getSearchedData('<li class="category\d+"> <strong>([^<]*)</strong>', data).strip()

            products = self.regex.getAllSearchedData('(?i)<div class="listing-item[^"]*?">(.*?)</div>', data)
            if products and len(products) > 0:
                print len(products)
                #                self.totalProducts += len(products)
                #                self.logger.debug('Total Products for %s is [%s]' % (str(len(products)), self.totalProducts))
                self.notifyProduct.emit('<font color=green><b>Total Products Found [%s] for category[%s]</b></font>' % (
                    str(len(products)), category4Name))
                for product in products:
                    productDetailUrl = self.regex.getSearchedData('(?i)<a href="([^"]*)"', product)
                    if productDetailUrl not in self.dupCsvRows0:
                        self.totalProducts += 1
                        self.dupCsvRows0.append(productDetailUrl)
                        self.scrapProductDetails(productDetailUrl, category1Name, category2Name, category3Name,
                            category4Name)
                    else:
                        self.notifyProduct.emit(
                            '<font color=green><b>Already Exists This Product Under Category[%s]. Skip It.</b></font>' % category4Name)

                self.notifyProduct.emit(
                    '<font color=green><b>Total Products Scraped [%s].</b></font>' % str(self.totalProducts))

    def scrapProductDetails(self, url, category1Name, category2Name, category3Name, category4Name):
        self.logger.debug('Product Detail URL: ' + url)
        self.notifyProduct.emit('<b>Try to scrap product details under Category[%s]</b>' % category4Name)
        self.notifyProduct.emit('<font color=green><b>Product Detail URL: %s</b></font>' % url)
        data = self.spider.fetchData(url)
        if data and len(data) > 0:
            data = self.regex.reduceNewLine(data)
            data = self.regex.reduceBlankSpace(data)
            manufacturer = self.regex.getSearchedData(
                '(?i)<span class="manufacturer-box-label">Manufacturer:</span>([^<]*)</p>', data)
            productCode = self.regex.getSearchedData(
                '(?i)<span class="manufacturer-box-label">Model No:</span>([^<]*)</p>',
                data)
            if productCode not in self.dupCsvRows:
                self.totalProducts += 1
                self.dupCsvRows.append(productCode)
            else:
                self.notifyProduct.emit(
                    '<font color=green><b>Already Exists This Product Under Category[%s]. Skip It.</b></font>' % category4Name)
                return
            productName = self.regex.getSearchedData('(?i)<div class="product-name"> <h1>([^<]*)</h1>', data)
            productTechnicalDesc = self.regex.getSearchedData('(?i)<div class="product-short-description">([^<]*)</div>'
                , data)
            productDescriptions = self.regex.getSearchedData('(?i)<div class="product-specs">(.*?)</div>', data)
            productShortDesc = ''
            productFullDesc = ''
            if productDescriptions and len(productDescriptions) > 0:
                print 'desc: ' + productDescriptions
                productShortDesc = self.regex.getSearchedData('(?i)<p>(.*?)</p>', productDescriptions)
                productFullDesc = '\n'.join(
                    self.regex.getAllSearchedData('(?i)<li>([^<]*)</li>', productDescriptions))
            listPriceChunk = self.regex.getSearchedData('(?i)<div class="rrp-price regular-price">(.*?)</div>', data)
            listPrice = ''
            if listPriceChunk and len(listPriceChunk) > 0:
                listPrice = self.regex.getSearchedData('(?i)([0-9,.]+)', listPriceChunk)

            savePriceChunk = self.regex.getSearchedData('(?i)<div class="regular-price saving-price">(.*?)</div>', data)
            savePrice = ''
            if savePriceChunk and len(savePriceChunk) > 0:
                savePrice = self.regex.getSearchedData('(?i)([0-9%]+)', savePriceChunk)

            priceChunk = self.regex.getSearchedData('(?i)<div class="[^"]*" id="product-price-\d+">(.*?)</div>', data)
            price = ''
            if priceChunk and len(priceChunk) > 0:
                price = self.regex.getSearchedData('(?i)([0-9,.]+)', priceChunk)

            deliveryChunk = self.regex.getSearchedData('(?i)<div class="delivery">(.*?)</div>', data)
            delivery = ''
            if deliveryChunk and len(deliveryChunk) > 0:
                delivery = self.regex.getSearchedData('(?i)<p>([^<]*)</p>', deliveryChunk)

            warrantyChunk = self.regex.getSearchedData('(?i)<div class="warranty">(.*?)</div>', data)
            warranty = ''
            if warrantyChunk and len(warrantyChunk) > 0:
                warranty = self.regex.getSearchedData('(?i)<p>([^<]*)</p>', warrantyChunk)

            ## Download and save product images
            productImageUrl = self.regex.getSearchedData(
                '(?i)src="(http://assets.cs-catering-equipment.co.uk/media/catalog/product/cache/1/image/256x/[^"]*)"',
                data)
            print productImageUrl
            productImage = self.regex.getSearchedData('(?i)/([a-zA-Z0-9-_.]*)$', productImageUrl)
            if productImage and len(productImage) > 0:
                print productImage
                self.notifyProduct.emit(
                    '<font color=green><b>Downloading Product Image [%s]. Please wait...</b></font>' % productImage)
                self.downloadFile(productImageUrl, 'product_image/' + productImage)
                self.notifyProduct.emit('<font color=green><b>Downloaded Product Image [%s].</b></font>' % productImage)
                #                self.utils.downloadFile(productImageUrl, 'product_image/' + productImage)

            ## Download and save brand images
            brandImageUrl = self.regex.getSearchedData(
                '(?i)<div class="manufacturer-box-left"><a href="[^"]*"[^>]*?><img src="([^"]*)"', data)
            brandImage = ''
            if brandImageUrl and len(brandImageUrl) > 0:
                brandImageUrl = self.regex.replaceData('(?i)logo/', '', brandImageUrl)
                brandImage = self.regex.getSearchedData('(?i)/([a-zA-Z0-9-_.]*)$', brandImageUrl)
                if brandImage and len(brandImage) > 0:
                    self.notifyProduct.emit(
                        '<font color=green><b>Downloading Brand Image [%s]. Please wait...</b></font>' % brandImage)
                    #                    self.utils.downloadFile(brandImageUrl, 'brand_image/' + brandImage)
                    self.downloadFile(brandImageUrl, 'brand_image/' + brandImage)
                    self.notifyProduct.emit('<font color=green><b>Downloaded Brand Image [%s].</b></font>' % brandImage)

            csvData = [url, productCode, productName, manufacturer, listPrice, price, savePrice,
                       productShortDesc, productFullDesc, productTechnicalDesc, warranty, delivery,
                       productImage,
                       category1Name, category2Name, category3Name, category4Name, brandImage]

            self.csvWriter.writeCsvRow(csvData)
            self.logger.debug(unicode(csvData))
            self.notifyProduct.emit(
                '<font color=green><b>Total Products Scraped [%s].</b></font>' % str(self.totalProducts))
#            self.notifyProduct.emit('<b>Product Details: %s</b>' % unicode(csvData))


    def downloadFile(self, url, downloadPath, retry=0):
        print url
        self.notifyProduct.emit('<b>File URL: %s.</b>' % url)
        try:
            socket.setdefaulttimeout(10)
            opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),
                urllib2.HTTPHandler(debuglevel=0),
                urllib2.HTTPSHandler(debuglevel=0))
            opener.addheaders = [
                ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1')]
            urllib2.install_opener(opener)
            #            resp = opener.open(url, timeout=30)
            #            resp = urllib2.urlopen(url, timeout=30)
            resp = None
            try:
            #              resp =  urllib.urlopen(url)
                resp = opener.open(url, timeout=30)
            except Exception, x:
                print x
            if resp is None: return False

            print resp.info()
            print 'info.......'
            contentLength = resp.info()['Content-Length']
            contentLength = self.regex.getSearchedData('(?i)^(\d+)', contentLength)
            totalSize = float(contentLength)
            directory = os.path.dirname(downloadPath)
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                except Exception, x:
                    print x
            dl_file = open(downloadPath, 'wb')
            currentSize = 0
            CHUNK_SIZE = 32768
            totalSizeKB = totalSize / 1024 if totalSize > 0 else totalSize
            print 'everything ok............'
            while True:
                data = None
                try:
                    data = resp.read(CHUNK_SIZE)
                except Exception, x:
                    print x
                if not data:
                    break
                currentSize += len(data)
                dl_file.write(data)

                print('============> ' +\
                      str(round(float(currentSize * 100) / totalSize, 2)) +\
                      '% of ' + str(totalSize) + ' bytes')
                notifyDl = '===> Downloaded ' + str(round(float(currentSize * 100) / totalSize, 2)) + '% of ' + str(
                    totalSizeKB) + ' KB.'
                self.notifyProduct.emit('<b>%s</b>' % notifyDl)
                if currentSize >= totalSize:
                    dl_file.close()
                    return True
        except urllib2.HTTPError as x:
            error = 'Error downloading: ' + x
            self.notifyProduct.emit('<font color=red><b>%s</b></font>' % error)
        except Exception, x:
            error = 'Error downloading: ' + x
            self.notifyProduct.emit('<font color=red><b>%s</b></font>' % error)
            return False

