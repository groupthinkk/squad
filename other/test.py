import requests

API_KEY = 'CazMCDN5G2SuFhET3BuXdLIW01PQxisNLwKRIw'

def record_comparison(turk_id, comparison_id, choice_id, dec_miliseconds, ux_id):
    API_URL = "http://54.200.77.76/api/v0/predictions/instagram/"
    data = {
        'api_key': API_KEY,
        'turker_id': turk_id,
        'comparison_id': comparison_id,
        'choice_id': choice_id,
        'decision_milliseconds': dec_miliseconds,
        'ux_id': ux_id
    }
    req = requests.post(API_URL, data=data)
    print req.text
    return req.json()

if __name__ == '__main__':
    record_comparison("turker_0003", 1, 2605, 11, "1")