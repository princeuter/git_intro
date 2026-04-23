from faker import Faker

fake = Faker()


def generate_user():
    return {
        "name": fake.name(),
        "email": fake.email(),
        "address": fake.address(),
    }


if __name__ == "__main__":
    for _ in range(5):
        print(generate_user())
