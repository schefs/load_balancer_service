from locust import task, between
from locust.contrib.fasthttp import FastHttpUser


class MyUser(FastHttpUser):

    wait_time = between(0.1, 1)

    @task()
    def change_password(self):
        self.client.post("/changePassword", data="user = schef")

    @task()
    def register(self):
        self.client.post("/register", data="user = schef")

    @task()
    def login(self):
        self.client.get("/login")

    def on_start(self):
        self.login()

