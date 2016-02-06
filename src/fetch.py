import requests
import private

course_listing_request = requests.post(private.url, headers=private.headers, cookies=private.cookies, data=private.data)

f = open('output.html', 'w')
f.write(course_listing_request.text.encode('ascii', 'ignore'))
f.close()
