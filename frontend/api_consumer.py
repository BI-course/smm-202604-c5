import requests

# PART 1: GET 
print("PART 1: GET request (retrieve data)\n")



response = requests.get('https://api.stackexchange.com/2.3/questions?order=desc&sort=activity&pagesize=3&site=stackoverflow')

for data in response.json()['items']:
    print('=' * 50)
    print('Title: ', data['title'])
    print('Link: ', data['link'])
    print('Answer Count: ', data['answer_count'])
    print('=' * 50, '\n')


# PART 2: POST 
print("\nPART 2: POST request (create data), with headers\n")

create_url = 'https://jsonplaceholder.typicode.com/posts'

new_post = {
    'title': 'Learning APIs in BBT 4206',
    'body': 'This is a test post created from a Python script.',
    'userId': 1,
}

headers = {
    'Content-Type': 'application/json',  
    'Accept': 'application/json',        
}

response = requests.post(create_url, json=new_post, headers=headers)

print('Status Code:', response.status_code)  
print('Response Body:', response.json())


# PART 3: PUT 

print("\nPART 3: PUT request (update data)\n")

update_url = 'https://jsonplaceholder.typicode.com/posts/1'

updated_post = {
    'id': 1,
    'title': 'Updated Title',
    'body': 'This post has been updated.',
    'userId': 1,
}

response = requests.put(update_url, json=updated_post, headers=headers)

print('Status Code:', response.status_code)  
print('Response Body:', response.json())


# PART 4: DELETE 

print("\nPART 4: DELETE request (remove data)\n")

delete_url = 'https://jsonplaceholder.typicode.com/posts/1'

response = requests.delete(delete_url)

print('Status Code:', response.status_code)  




print("\nPART 5: GET request (compare historical rainfall)\n")

archive_url = 'https://archive-api.open-meteo.com/v1/archive'

nairobi_params = {
    'latitude': -1.2921,
    'longitude': 36.8219,
    'daily': 'precipitation_sum',
    'timezone': 'Africa/Nairobi',
}

seasons = {
    'Oct-Dec 1963 Short Rains': ('1963-10-01', '1963-12-31'),
    'El Nino (Oct-Dec 1997)': ('1997-10-01', '1997-12-31'),
    'Oct-Dec 2020 Short Rains': ('2020-10-01', '2020-12-31'),
    'Oct-Dec 2021 Short Rains': ('2021-10-01', '2021-12-31'),
    'Oct-Dec 2022 Short Rains': ('2022-10-01', '2022-12-31'),
    'Oct-Dec 2023 Short Rains': ('2023-10-01', '2023-12-31'),
    'Oct-Dec 2024 Short Rains': ('2024-10-01', '2024-12-31'),
    'Oct-Dec 2025 Short Rains': ('2025-10-01', '2025-12-31'),
  
}


for label, (start_date, end_date) in seasons.items():

   
    params = {**nairobi_params, 'start_date': start_date, 'end_date': end_date}

   
    response = requests.get(archive_url, params=params)

  
    daily_rainfall = response.json()['daily']['precipitation_sum']

   
    total_rainfall = sum(mm for mm in daily_rainfall if mm is not None)

    print('=' * 50)
    print(label)
    print('Total rainfall (mm):', round(total_rainfall, 1))
    print('=' * 50, '\n')
