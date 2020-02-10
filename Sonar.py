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
    #   @param sonarQubeImg is the Docker image for SonarQube server
    #   @param sonarScannerImg is the Docker image for sonarScanner
    #   @param host is ip adrress for the SonarQube server
    #   @param port is port number for SonarQube server
    #   @auth is login credentials for SonarQube server
    def __init__(self, sonarQubeImg='sonarqube',
                 sonarScannerImg='vesakoskela/sonar-scanner-maven',
                 host='127.0.0.1', port=9000, auth=('admin', 'admin')):

        self.sonarQubeImg = sonarQubeImg
        self.sonarScannerImg = sonarScannerImg
        self.dockerClient = docker.from_env()
        self.sonarQubeContainer = None
        self.sonarQubeRunning = False
        self.sonarScannerContainer = None
        self.host = host
        self.port = port
        self.url = 'http://' + host + ":" + str(port)
        self.auth = auth

    ##  startSonarQube
    #   @brief Method for starting sonarQube docker container
    #   @returns SonarError if exceptions occured
    #   SonarQube server is not necessarily responding after calling this
    #   method returns. Use isSonarQubeRunning to check if it's up.
    def startSonarQube(self):
        try:
            print("SonarQube server is starting...")
            if self.isSonarQubeRunning() is True:
                return
            else:
                self.sonarQubeContainer = self.dockerClient.containers.run(
                    self.sonarQubeImg,
                    detach=True,
                    ports={str(self.port) + '/tcp': self.port}
                )
            if self.sonarQubeContainer is None:
                raise SonarError()
        except (docker.errors.ContainerError, docker.errors.APIError, SonarError):
            raise SonarError("Error occured while starting SonarQube server!")

    ##  stopSonarQube
    #   @brief Method for stopping SonarQube
    #   @returns SonarError if errors occured
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
        except (docker.errors.ContainerError, docker.errors.APIError):
            raise SonarError("An exception occured while stopping SonarQube server!")

    ##  isSonarQubeRunning
    #   @brief Method for checking if SonarQube server is up
    #   @returns True only when SonarQube server HTTP response is 200
    #   This method is for purpose of waiting until SonarQube server is up and
    #   running.
    def isSonarQubeRunning(self):
        try:
            r = requests.head(self.url)
            if r.status_code == 200:
                self.sonarQubeRunning = True
                return True
            else:
                self.sonarQubeRunning = False
                return False
        except requests.ConnectionError:
            return False

    ##  runSonarScanner
    #   @brief Method for running SonarScanner for Maven.
    #   @param directory is the directory of the Java project
    #   @param *params is maven commands which are executed. 'mvn' is already
    #   included. Eg. if you want to run "mvn clean verify sonar:sonar", call
    #   runSonarScanner(directory, "clean", "verify", "sonar:sonar")
    #   @returns SonarError if errors occured.
    def runSonarScanner(self, directory, *params):
        try:
            mavenCommand = "mvn "
            for p in params:
                mavenCommand += p + " "
            mavenCommand += '-Dsonar.host.url=http://127.0.0.1:9000'
            print(mavenCommand)
            self.sonarScannerContainer = self.dockerClient.containers.run(
                self.sonarScannerImg,
                mavenCommand,
                network_mode="host",
                tty=True,
                auto_remove=True,
                detach=True,
                volumes={directory: {'bind': '/usr/src/mymaven', 'mode': 'rw'}},
                working_dir="/usr/src/mymaven"
            )
        except (docker.errors.ContainerError, docker.errors.APIError):
            raise SonarError("An Exception occured while running SonarScanner")

        # For debugging
        # Dirty hack. Log comes as byte stream and by default log prints too
        # much. With this it prints only [INFO], [WARNING], etc.
        newline = True
        print_next = True
        for line in self.sonarScannerContainer.logs(stream=True):
            a = line.decode()
            if a == "\n":
                newline = True
            else:
                if newline is True:
                    newline = False
                    if a == "[":
                        print(a)
                        print_next = True
                    else:
                        print_next = False
                if print_next is True:
                    print(a, end="")


# For testing
if __name__ == "__main__":
    auth_test = ('admin', 'admin')
    url_test = '127.0.0.1'
    port_test = 9000
    sonarObject = Sonar()
    try:
        sonarObject.startSonarQube()
        sonarObject.runSonarScanner("/home/veko/UniStuff/commons-cli", "sonar:sonar")
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
