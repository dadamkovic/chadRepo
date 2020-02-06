import docker
import requests
import time

##  Sonar
#   @brief class for handling SonarQube and SonarScanner for Maven
class Sonar:

    ##  The Constructor
    def __init__(self):
        self.client = docker.from_env()
        self.sonarQubeContainer = None
        self.sonarQubeRunning = False

    ##  startSonarQube
    #   @brief Method for starting sonarQube docker container
    #   SonarQube server is not up yet after calling this method.
    #   Use isSonarQubeRunning to check if it's up.
    def startSonarQube(self):
        print("SonarQube is starting..")
        if self.isSonarQubeRunning() is False:
            self.sonarQubeContainer = self.client.containers.run(
                "sonarqube",
                detach=True,
                name="sonarqube",
                ports={'9000/tcp': 9000}
            )

    ##  stopSonarQube
    #   @brief Method for stopping SonarQube
    #   Stops SonarQube docker container and removes it
    def stopSonarQube(self):
        self.sonarQubeContainer.stop(timeout=3600)

        while self.sonarQubeContainer.status != "exited":
            self.sonarQubeContainer.reload()
            time.sleep(1)
        self.sonarQubeContainer.remove()
        self.sonarQubeRunning = False

    ##  isSonarQubeRunning
    #   @brief Method for checking if SonarQube server is up
    #
    #   @returns True only when SonarQube server HTTP response is 200
    def isSonarQubeRunning(self):
        try:
            r = requests.head("http://127.0.0.1:9000")
            if r.status_code == 200:
                self.sonarQubeRunning = True
                return True
            else:
                self.sonarQubeRunning = False
                return False
        except requests.ConnectionError:
            return False


"""
sonar = Sonar()
sonar.startSonarQube()
while sonar.isSonarQubeRunning() is False:
    print(".", sep="", end="", flush=True)
    time.sleep(2)
print("SonarQube is Up!")
sonar.stopSonarQube()
"""
