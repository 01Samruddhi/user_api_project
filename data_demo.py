from faker import Faker

faker = Faker()

user = {
    "id": 1,
    "name": "Daisy",
    "email": "daisy@gmail.com"
}

users = [
    user, {
        "id": 2,
        "name": "Sakura",
        "email": "blossom@gmail.com"    
    },
]

filtered = [u for u in users if u["name"]=="Daisy"]

users.append({"id":3,"name":"Mapal","email":"leaf@gmail.com"})

for u in users:
    if u["id"]==2:
        u["email"]="cherry@gmail.com"

users = [u for u in users if u["id"]!=1]

for i in range(5):
    users.append({
        "id": i+10,
        "name": faker.name(),
        "email": faker.unique.email(),
        })
print(users)


# user = {
#     "name":faker.name(),
#     "email":faker.email()
# }
# print("Created User",user)

# users = []
# for _ in range(5):
#     users.append({
#         "name":faker.name(),
#         "email":faker.email()
#     })
# print("\nList of Users:")
# for u in users:
#     print(u)

# print("\nFilter user name:")
# for u in users:
#     if "Daisy" in u["name"]:
#         print(u)


