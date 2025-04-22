import jwt
import time

METABASE_SITE_URL = "https://metabase.hoctiep.com"
METABASE_SECRET_KEY = "24bb62620608f89e31661876fa61ac57b7946af35c3979bb33c60c9ad35257b6"

payload = {
  "resource": {"dashboard": 3},
  "params": {
    
  },
}
token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#bordered=true&titled=true"

print(iframeUrl)