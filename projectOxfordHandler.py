import requests
import time
import logging
import numpy as np
import cv2
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import os

class ProjectOxfordHandler():

    def __init__(self, token, url):
        """init"""
        self._maxNumRetries = 10
        self.url = url
        self.token = token
        sel.max_height = 3200


    def processRequest(self, json, data, headers, params ):
        """
        Helper function to process the request to Project Oxford

        Parameters:
        json: Used when processing images from its URL. See API Documentation
        data: Used when processing image read from disk. See API Documentation
        headers: Used to pass the key information and the data type request
        """

        retries = 0
        result = None

        while True:
            response = requests.request( 'post', self.url, json = json, data = data, headers = headers, params = params )

            if response.status_code == 429:
                logging.info( "Message: %s" % ( response.json() ) )
                if retries <= self._maxNumRetries: 
                    time.sleep(1) 
                    retries += 1
                    continue
                else: 
                    logging.error( 'Error: failed after retrying!' )
                    break
            elif response.status_code == 202:
                result = response.headers['Operation-Location']
            else:
                logging.error( "Error code: %d" % ( response.status_code ) )
                logging.error( "Message: %s" % ( response.json() ) )
            break
            
        return result

    def getOCRTextResult( self, operationLocation, headers ):
        """
        Helper function to get text result from operation location

        Parameters:
        operationLocation: operationLocation to get text result, See API Documentation
        headers: Used to pass the key information
        """

        retries = 0
        result = None

        while True:
            response = requests.request('get', operationLocation, json=None, data=None, headers=headers, params=None)
            if response.status_code == 429:
                logging.info("Message: %s" % (response.json()))
                if retries <= self._maxNumRetries:
                    time.sleep(1)
                    retries += 1
                    continue
                else:
                    logging.error('Error: failed after retrying!')
                    break
            elif response.status_code == 200:
                result = response.json()
            else:
                logging.error("Error code: %d" % (response.status_code))
                logging.error("Message: %s" % (response.json()))
            break

        return result

    def showResultOnImage( self, result , filename):
        """Display the obtained results onto the input image"""
        with open(filename, 'rb') as f:
            data = f.read()
        data8uint = np.fromstring(data, np.uint8)  # Convert string to an unsigned int array
        img = cv2.cvtColor(cv2.imdecode(data8uint, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        img = img[:, :, (2, 1, 0)]
        fig, ax = plt.subplots(figsize=(12, 12))
        ax.imshow(img, aspect='equal')

        lines = result['recognitionResult']['lines']

        for i in range(len(lines)):
            words = lines[i]['words']
            for j in range(len(words)):
                tl = (words[j]['boundingBox'][0], words[j]['boundingBox'][1])
                tr = (words[j]['boundingBox'][2], words[j]['boundingBox'][3])
                br = (words[j]['boundingBox'][4], words[j]['boundingBox'][5])
                bl = (words[j]['boundingBox'][6], words[j]['boundingBox'][7])
                text = words[j]['text']
                x = [tl[0], tr[0], tr[0], br[0], br[0], bl[0], bl[0], tl[0]]
                y = [tl[1], tr[1], tr[1], br[1], br[1], bl[1], bl[1], tl[1]]
                line = Line2D(x, y, linewidth=3.5, color='red')
                ax.add_line(line)
                ax.text(tl[0], tl[1] - 2, '{:s}'.format(text),
                bbox=dict(facecolor='blue', alpha=0.5),
                fontsize=14, color='white')

        plt.axis('off')
        plt.tight_layout()
        plt.draw()
        filename = os.path.splitext(filename)[0] + "_annotated" + os.path.splitext(filename)[1]
        plt.savefig(filename, format='png')
        return filename

    def getTextFileFromResult(self, result, filename):
        """Writes the found text entities to a text file"""
        filename = os.path.splitext(filename)[0] + "_text.txt"
        with open(filename, 'w') as f:

            lines = result['recognitionResult']['lines']

            for i in range(len(lines)):
                words = lines[i]['words']
                for j in range(len(words)):
                    text = words[j]['text'] + " "
                    f.write(text)
                f.write("\n")
        return filename

    def getResultForImage(self, filename):
        """Process the image"""
        self.resize_image(filename)
        with open(filename, 'rb') as f:
            data = f.read()

        # Computer Vision parameters
        params = {'handwriting' : 'true'}

        headers = dict()
        headers['Ocp-Apim-Subscription-Key'] = self.token
        headers['Content-Type'] = 'application/octet-stream'

        json = None

        operationLocation = self.processRequest(json, data, headers, params)

        result = None
        if (operationLocation != None):
            headers = {}
            headers['Ocp-Apim-Subscription-Key'] = self.token
            while True:
                time.sleep(1)
                result = self.getOCRTextResult(operationLocation, headers)
                if result['status'] == 'Succeeded' or result['status'] == 'Failed':
                    break

        # Load the original image, fetched from the URL
        if result is not None and result['status'] == 'Succeeded':
            return result

    def resize_image(self, filename):
        """Rescale `image` to `target_height` (preserving aspect ratio)."""
        image = cv2.imread(filename)

        height, width = image.shape[:2]
        max_height = 3200
        max_width = 3200

        # only shrink if img is bigger than required
        if max_height < height or max_width < width:
            # get scaling factor
            scaling_factor = max_height / float(height)
            if max_width/float(width) < scaling_factor:
                scaling_factor = max_width / float(width)
            # resize image
            image = cv2.resize(image, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
        cv2.imwrite(image, filename)