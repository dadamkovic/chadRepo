import docker
import requests
import time

class SonarError(Exception):
    def __init__(self, message="SonarError"):
        self.message = message
##  Sonar
#   @brief class for handling SonarQube and SonarScanner for Maven
class Sonar:

    ##  The Constructor
    #   @param host is ip adrress for the SonarQube server
    #   @param port is port number for SonarQube server
    #   @auth is login credentials for SonarQube server
    def __init__(self, host='127.0.0.1', port=9000, auth=('admin', 'admin')):
        self.dockerClient = docker.from_env()
        self.sonarQubeContainer = None
        self.sonarQubeRunning = False
        self.sonarScannerContainer = None
        self.host = host
        self.port = port
        self.url = "http://" + host + str(port)
        self.auth = auth

    ##  startSonarQube
    #   @brief Method for starting sonarQube docker container
    #   @returns SonarError if exceptions occured
    #   SonarQube server is not necessarily responding after calling this
    #   method returns. Use isSonarQubeRunning to check if it's up.
    def startSonarQube(self):
        try:
            print("SonarQube server is starting...")
            if self.isSonarQubeRunning() is False:
                self.sonarQubeContainer = self.dockerClient.containers.run(
                    "sonarqube:latest",
                    detach=True,
                    ports={str(self.port) + '/tcp': self.port}
                )
            if self.sonarQubeContainer is None:
                raise SonarError()
        except (docker.errors.ContainerError, docker.errors.APIError, SonarError):
            raise SonarError("Error occured while starting SonarQube server!")

    ##  stopSonarQube
    #   @brief Method for stopping SonarQube
    #   @returns SonarError if errors
    #   Stops SonarQube docker container and removes it. SonarQube server
    #   docker container should be still stopped and removed even if errors
    #   are returned.
    def stopSonarQube(self):
        try:
            self.sonarQubeContainer.stop(timeout=3600)
            print("SonarQube server is stopping...")
            while self.sonarQubeContainer.status != "exited":
                self.sonarQubeContainer.reload()
                time.sleep(1)
            self.sonarQubeContainer.remove()
            self.sonarQubeRunning = False
            print("SonarQube server stopped and docker container removed.")
        except (docker.errors.ContainerError, docker.errors.APIError, Exception) as e:
            print("Error occured while stopping SonarQube server!")

    ##  isSonarQubeRunning
    #   @brief Method for checking if SonarQube server is up
    #   @returns True only when SonarQube server HTTP response is 200
    #   This method is for purpose of waiting until SonarQube server is up and
    #   running.
    def isSonarQubeRunning(self, url):
        try:
            r = requests.head(url)
            if r.status_code == 200:
                self.sonarQubeRunning = True
                return True
            else:
                self.sonarQubeRunning = False
                return False
        except requests.ConnectionError:
            return False

    ##  buildMavenProject
    #   @brief builds the Maven project
    def buildMavenProject(self):
        self.sonarScannerContainer = self.dockerClient.run(
            "vesakoskela/sonar-scanner-maven",
            "mvn",
            "clean",
            "verify",
            network_mode="host",
            tty=True,
            auto_remove=True,
            volumes={'$(pwd)': {'bind': ':/usr/src/mymaven', 'mode': 'rw'}},
            working_dir="/usr/src/mymaven"
        )

    def runSonarScanner(self):
        self.sonarScannerContainer = self.dockerClient.run(
            "vesakoskela/sonar-scanner-maven",
            "mvn",
            "sonar:sonar",
            network_mode="host",
            tty=True,
            auto_remove=True,
            volumes={'$(pwd)': {'bind': ':/usr/src/mymaven', 'mode': 'rw'}},
            working_dir="/usr/src/mymaven"
        )


if __name__ == "__main__":
    auth_test = ('admin', 'admin')
    url_test = '127.0.0.1'
    port_test = 9000
    sonar = Sonar(url_test, port_test, auth_test)
    try:
        sonar.startSonarQube()
    except SonarError as e:
        print(e.message)

    """
    while sonar.isSonarQubeRunning() is False:
        print(".", sep="", end="", flush=True)
        time.sleep(2)
    print("SonarQube is Up!")
    input("Press any key to STOP")
    """
# sonar.stopSonarQube()
