import requests
r = requests.post('http://127.0.0.1:5000/api/pipeline/calculate_score', json={'customer_id':'CUST_MSM_00001'})
print('status', r.status_code)
print(r.text)
