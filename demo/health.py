from lean_runner import LeanClient

if __name__ == "__main__":
    client = LeanClient("localhost:50051")
    print(client.health_check())
