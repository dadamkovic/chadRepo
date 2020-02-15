Alpha version of the Spint 1 software.

Contains the GUI implementation core of the application. GUI specification file is only local to this and shouldn't 
end up in the final application.

----------------------------------------------
QUICK INSTALL:

1. python setup.py

----------------------------------------------


Sami specific info:

I tried to make it a all as straightforward as possible for you with plenty of comments.
I also added the .ui file if you wanted to donwload the qt designer and see the names
of the widgets in more user friendly way, but the naming conventions should be pretty 
consistent. The whole funcitonality of the GUI is enclosed in UserInterface class you shouldn't 
really need anything else as far as I can tell. Most of it you won't have to touch you pretty much just need
to bind the sonarqube button and maybe do something with with the progress bar to let the user know something is
going on.

Relevant class variables:

self.run_sonar_button
self.sonarqube_progress_group
self.sonarqube_progress_bar
self.sonarqube_status
self.repo_list[<repo index>]['tools']     --interface to the git class methods

