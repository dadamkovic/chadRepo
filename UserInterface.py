#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 14:29:58 2020

@author: daniel
"""
from qtGUIsetup import Ui_CodeAnalysisTool
from PyQt5 import QtCore, QtGui, QtWidgets
from copy import copy
import GitRepo as grepo
import shutil

# For analysis
import os
from Sonar import Sonar
from sonarAPI import API
from analysisParser import analysisParseList

# Could be moved to something like utils, if more functions like this are made
from main import wait


class RepoElements():
    def __init__(self):
        self.repo_url = ""
        


class UserInterface(Ui_CodeAnalysisTool):
    def __init__(self,CodeAnalysisTool):
        super(UserInterface,self).__init__()
        self.setupUi(CodeAnalysisTool)
        
        #these will hold information about repos, also declares self.active_repo
        self.repo_list, self.active_repo = self._default_repo_setup()

        #binds widgets to functions
        self.bindActiveWidgets()
        
        
    
    
    ##Binds widgets to the methods that process inputs
    def bindActiveWidgets(self):
        #events that change how the  active screeen changes
        self.repo_screen_butt.clicked.connect(lambda :self.menuScreenSel(0))
        self.sonar_screen_butt.clicked.connect(lambda :self.menuScreenSel(1))
        self.cs_screen_butt.clicked.connect(lambda :self.menuScreenSel(2))
        self.pmd_screen_butt.clicked.connect(lambda :self.menuScreenSel(3))
        self.settings_screen_butt.clicked.connect(lambda :self.menuScreenSel(4))
        
        #all bellow are buttons for folder selection
        self.sonar_save_dirsel.clicked.connect(lambda : self.docBrowser(0))
        self.cs_save_dirsel.clicked.connect(lambda : self.docBrowser(1))
        self.pmd_save_dirsel.clicked.connect(lambda : self.docBrowser(2))
        self.repo_save_dirsel.clicked.connect(lambda : self.docBrowser(3))

        # Buttons for running analyzers
        self.run_sonar_button.clicked.connect(self.analyseSonar)
        
        #user clicked the repo submit button, repo gets downlaoded and default branch gets set
        self.git_repo_input_submit.clicked.connect(self.readRepoUrl)
        
        #enables user input box and folder sel button at the same time
        self.repo_save_enable_butt.toggled.connect(self._enableSave)
        
        #switching repos
        self.tabWidget.currentChanged.connect(lambda : self.switchRepoContext(self.tabWidget.currentIndex()))
        
        #triggered if user selects different branch
        self.branch_selector.currentTextChanged.connect(self.switchBranch)
        
        self.repo_save_dir.textChanged.connect(self._updateSaveDir)
        print("Init complete")
        
    #every time user types into the input field this gets updated
    def _updateSaveDir(self):
        self.active_repo['save_dir'] = self.repo_save_dir.text()
    
    ##when user switches saving on or off we want to track it and change stuff
    def _enableSave(self):
        toggler = self.active_repo['keep']
        self.repo_save_enable_butt.setEnabled(not toggler)
        self.repo_save_dirsel.setEnabled(not toggler)
        self.repo_save_dir.setEnabled(not toggler)
        self.active_repo['keep'] = not toggler
        
    ##called when user changes branches in the dropdown menu
    def switchBranch(self):
        if self.active_repo['tools'] == None:   #dont do anything if the branches arent loaded yet
            return
        
        new_branch = self.branch_selector.currentText()
        self.active_repo['tools'].change_branch(new_branch)
        self.active_repo['active_branch'] = new_branch
        #update info about the last commit in branch
        commit_data = self.active_repo['tools'].get_commit_data()
        info_text = self.prettyDict(commit_data)
        self.active_repo['data'] = info_text
        self.repo_info.setText(self.active_repo['data'])
        
    ##Called when the user switches between the top tabs
    #@param[in] repo_idx Index specifying which repo needs to be displayed
    def switchRepoContext(self, repo_idx):
        #we copy the current active repo into the correct repo memory slot
        #this might not be needed since I can just bind the memory togetger but this 
        #explicit way is clearer
        self.repo_list[self.active_repo['idx']] = copy(self.active_repo) 
        self.active_repo = copy(self.repo_list[repo_idx])
        
        #if the repo is already loaded lock repo url input and load values into widgets
        if self.active_repo['init'] :
            self.git_repo_input.setEnabled(False)
            self.git_repo_input_submit.setEnabled(False)
            self.branch_selector.addItems(self.active_repo['branches'])
            self.git_repo_input.setText(self.active_repo['url'])
            self.repo_info.setText(self.active_repo['data'])
            self.branch_selector.setCurrentText(self.active_repo['active_branch'])
        #clear uninitialized widgets
        else:
            self.git_repo_input.setEnabled(True)
            self.git_repo_input_submit.setEnabled(True)
            self.branch_selector.clear()
            self.git_repo_input.setText("")
            self.repo_info.setText("")
            
        #enables/disables save input as neccessary
        if self.active_repo['keep']:
            self.repo_save_dir.setEnabled(True)
        else:
            self.repo_save_dir.setEnabled(False)
        
        #this can only be "" if we havent loaded anything in yet
        if self.active_repo['save_dir'] != "":
            self.repo_save_dir.setText(self.active_repo['save_dir'])
        else:
            self.repo_save_dir.setText("")
        
    ##Gets called only once for every repository
    #Currently it is not possible to load a different repository once we load something
    def readRepoUrl(self):
        
        self.active_repo['url'] = self.git_repo_input.text()
        self.active_repo['save_dir'] = self.repo_save_dir.text()
        
        if self.active_repo['save_dir'] == '':
            self.active_repo['save_dir'] = './work/repo{}'.format(self.active_repo['idx'])
        self.active_repo['created_in'] = self.active_repo['save_dir']
            
        git_repo = grepo.GitRepo(self.active_repo['save_dir'])
        self.active_repo['tools'] = git_repo
        
        self.active_repo['tools'].pull_repo_contents(self.active_repo['url'])
        
        commit_data = self.active_repo['tools'].get_commit_data()
        info_text = self.prettyDict(commit_data)
        self.active_repo['data'] = info_text
        self.repo_info.setText(self.active_repo['data'])
        
        self.active_repo['branches'] = commit_data['branches']
        self.branch_selector.addItems(self.active_repo['branches'])
        
        self.branch_selector.setEnabled(True)
        self.label.setEnabled(True)
        
        #user should NOT be able to change url of the repo after loading it
        self.active_repo['init'] = True
        self.git_repo_input.setEnabled(False)
        self.git_repo_input_submit.setEnabled(False)
    
    ## analyseSonar
    #  @brief Takes parameters from GUI and runs the current(14.2.) main function with them
    #  @details Literally copypasta from current(14.2.) main and changed command line parameters to the GUI ones.
    #           NOTE: This could be done in a separate module to be used by both, main and GUI.
    def analyseSonar(self):
        # Start SonarQube and API for it
        sonar = Sonar(sonarScannerImg='sonar-maven')
        if not sonar.isSonarQubeRunning():
            sonar.startSonarQube()
        api = API()

        # Get the save dir and make the git path with it
        save_dir = self.sonar_save_dir_input.text()
        if os.path.isabs(save_dir):
            git_full_path = os.path.join(save_dir, active_repo['created_in'])
        else:
            git_full_path = os.path.join(os.getcwd(), active_repo['created_in'])
        print('active_repo['created_in']:', git_full_path)

        wait('sonarqube', sonar.isSonarQubeRunning, timeout=5)

        # Running Sonar scanner(with sanity check)
        before = set(api.projects())
        print(before)
        sonar.runSonarScanner(git_full_path, 'clean', 'verify', 'sonar:sonar')

        wait('analysis', lambda: before.symmetric_difference(api.projects()), timeout=1)

        project_key = before.symmetric_difference(api.projects()).pop()
        print('project_key:', project_key)

        wait('issues', lambda: any(api.issues(project=project_key)), timeout=1)

        # Get the issues from API, parse and save as csv
        issues = list(api.issues(project=project_key))
        issue_file = os.path.join(save_dir,  active_repo['created_in'] + '_issues.csv')
        analysisParseList(issues, issue_file) # NOTE: NOT TESTED!   Parse and write to file

        # Get the git commit data
        commit_file = os.path.join(save_dir,  active_repo['created_in'] + '_commits.csv')
        # TODO: get commit data for each commit associated with an issue
        #           and write to file
        print(len(issues))
        print(issue_file)
        print(commit_file)
        api.delete_project(project_key)

        # WARNING: The cleanup() doesn't stop SonarQube yet
    
    ##Used to switch between user views (repo, )
    #param[in] index Number representing the menu screen
    def menuScreenSel(self,index):
        self.stackedWidget.setCurrentIndex(index)
        
    ##Initializes the repo list 
    def _default_repo_setup(self):
        repo_list = []
        for num in range(6):
            repo = {}
            repo['init'] = False            #repo loaded
            repo['keep'] = False            #save/not save
            repo['url'] = ""                #repo url
            repo['branches'] = ""           #all branches
            repo['active_branch'] = ""      #currently selected branch
            repo['save_dir'] = ""           #holds where to save the repo
            repo['data'] = ""               #string info about the branch
            repo['tools'] = None            #holds git repo class instance
            repo['idx'] = num               #index of the repo
            repo['created_in'] = ""         #if this and save_dir are different contents may have to be copied before exit
            repo_list.append(repo)
        active_repo = repo_list[-1]
        active_repo['idx'] = 0
        return repo_list[:-1], active_repo
    
    ##calls standard document browser and sets the info field with the chosen path
    def docBrowser(self,idx):
        folder = str(QtWidgets.QFileDialog.getExistingDirectory(self.centralwidget, "Select Directory"))        
        if idx == 0:
            self.sonar_save_dir_input.setText(folder)
        elif idx == 1: 
            self.cs_save_dir_input.setText(folder)
        elif idx == 2:
            self.pmd_save_dir_input.setText(folder)
        elif idx == 3:
            self.repo_save_dir.setText(folder)
            self.active_repo['save_dir'] = folder
            
        
    ##Used to print dict contents into information field in a resonably nice way
    #@note could probably just be used as private method
    def prettyDict(self,some_dict):
        output = ''
        for key, item in some_dict.items():
            output += str(key) + " : " + str(item) + "\n"
        return output
    
    ##Runs on exit and cleans workspace
    def cleanup(self):
        self.repo_list[self.active_repo['idx']] = self.active_repo
        for item in self.repo_list:
            file_dir = item['created_in']
            if not item['keep'] and file_dir != '':
                shutil.rmtree(file_dir)
                print("Removed" + file_dir)
            elif file_dir != item['save_dir']:
                shutil.move(item['created_in'],item['save_dir'])
        