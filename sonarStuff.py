import docker
import requests


class Sonar:
    def __init__(self):
        self.client = docker.from_env()
        self.sonarQubeContainer = "Null"
        self.sonarQubeRunning = False

    def startSonarQube(self):
        print("starting sonarqube")
        if self.isSonarQubeRunning() is False:
            print("sonar")
            self.sonarQubeContainer = self.client.containers.run(
                "sonarqube", detach=True,
                name="sonarqube",
                ports={'9000/tcp': 9000}
            )
            """
            for line in self.sonarQubeContainer.logs(stream=True):
                print(line.strip())
                """

    def stopSonarQube(self):
        self.sonarQubeContainer.stop()

    def isSonarQubeRunning(self):
        print("is sonar running")

        try:
            r = requests.head("http://127.0.0.1")
            print(r.status_code)
            if r.status_code == 200:
                self.sonarQubeRunning = True
                return True
            else:
                self.sonarQubeRunning = False
                return False
        except requests.ConnectionError:
            print("failed to connect")
        return False


sonar = Sonar()
sonar.startSonarQube()
