MAX_PRICE = 900 #цену указывать в копейках(1 руб = 100 копеек)
MIN_VOLUME = 300 #минимальный объем продаж(должно быть больше 0)
MIN_PROFIT = 4 #минимальный процент профита(должно быть больше 0)
DEPTH = 20
SLEEP_DELAY = 7 #время задержки между запросами
BAN_SLEEP_DELAY = 180

api_key = 'BF57CA42262C7D515A14A0380C6463E0'

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 OPR/72.0.3815.400"}
cookies = {
    "sessionid": "9182a070c30d477b0d5b22c5",
    "timezoneOffset": "10800,0",
    "_ga": "GA1.2.1309132490.1605793173",
    "Steam_Language": "russian",
    "steamCountry": "UA%7C8c7cf4e447d52992a1d1d5ef58af4a74",
    "_gid": "GA1.2.1821399530.1606745549",
    "steamMachineAuth76561199087634463": "C08E5133E18F946C831AB81E29143B389E82B39D",
    "steamRememberLogin": "76561199087634463%7C%7Cb020d45b13b1b947f98ae7f42be430fa",
    "browserid": "2164505684816642056",
    "webTradeEligibility": "%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A7%2C%22time_checked%22%3A1606746403%7D",
    "app_impressions": "753@2_100100_100101_100106",
    "steamLoginSecure": "76561199087634463%7C%7C67AD69961DEB2F7CD4F0A220445EF9E3C9BFE4CF"
  }