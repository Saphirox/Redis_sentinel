# generate_siege_urls.py

total_requests = 10000  # Adjust this number as needed
concurrent_users = 10
repetitions_per_user = total_requests // concurrent_users

with open("siege_urls.txt", "w") as file:
    for i in range(1, total_requests + 1):
        file.write(f"http://localhost:8008/set POST {{\"key\":\"test{i}\", \"value\":\"Hello World\"}}")
