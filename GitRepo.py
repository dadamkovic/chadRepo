#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 16:10:52 2020

@author: daniel
"""
import git
import os
import shutil
import time
from pandas import DataFrame

curr_work_dir = os.path.join(os.getcwd(), 'tmpRepo')

## Class that provides the neccessary funcitonality associated with git repos
class GitRepo():
    
    ## creates empty repository, pulled repositories will be stored here
    def __init__(self,work_dir=curr_work_dir,remote_url=''):
        self.work_dir = work_dir
        self.repo_url = remote_url
        
    def __enter__(self):
        if self.repo_url != '':
            self.pullRepoContents(remote_url=self.repo_url)
            return self
        
    ## @brief Cleanup repo before exit
    def __exit__(self, exc_type, exc_val, exc_tb):
        if(os.path.isdir(self.work_dir)):
            shutil.rmtree(self.work_dir)
            
    ## @brief Downloads the repo contents
    #  @param remote_url Reporsitory url (by default this is None)
    #  @param username Needed in case of pass protected repo
    #  @param password Needed in case of pass protected repo
    #  @returns True if repo pulled successfuly, False otherwise
    #
    #  The method will check if the repostitory is in valid format and create
    #  workRepo with contents of the user specified directory. If the repo
    #  is password protected it will request user input (password can also be
    #  specified as input arg).
    def pullRepoContents(self,remote_url=None,username=None,password=None):
        try:
            self._repoUrlTest(remote_url)   # testing the url for validity
        except UrlException as exc:
            print(exc)
            return False
        self.repo_url = remote_url

        try:
            filled_repo = git.Repo.clone_from(self.repo_url,self.work_dir)

        #entered when private repo, wrong path or non empty dir
        except git.cmd.CommandError:
			
            print("ERROR directory " + self.repo_url + 
                  " exists and not empty / pass protected git"
                  )
            
            #add username and pass to the remote url
            unlocked_url = self._getPass(self.repo_url,username,password)
            print("Trying to unlock")
            filled_repo = git.Repo.clone_from(unlocked_url,self.work_dir)

        self.filled_repo = filled_repo      # save the created repo information
        return True

    ## @brief Returns the dictionary with all the neccessary information
    def getCommitData(self, detached_name=''):
        commit_info = {}
        self.commit_handle = self.filled_repo.head.commit
        time_struct = time.gmtime()
        date_author = time.strftime("%Y-%m-%dT:%H:%M:%SZ",time_struct)
        time_struct = time.gmtime(self.commit_handle.committed_date)
        date_commiter = time.strftime("%Y-%m-%dT:%H:%M:%SZ",time_struct)

        self.commit_handle = self.filled_repo.head.commit
        
        #-4 to remove .git ending
        commit_info['project_id'] = self.repo_url.split('/')[-1][:-4]   
        commit_info['hash'] = self.commit_handle.hexsha
        commit_info['message'] = self.commit_handle.message
        commit_info['author'] = self.commit_handle.author.name
        commit_info['author_date'] = date_author
        
        timezone = self.commit_handle.author_tz_offset/3600
        commit_info['author_timezone'] = timezone
        commit_info['commiter'] = self.commit_handle.committer.name
        commit_info['commiter_date'] = date_commiter
        
        timezone = self.commit_handle.committer_tz_offset/3600
        commit_info['commiter_timezone'] = timezone
        
        beanch_list = self.filled_repo.remotes.origin.refs
        commit_info['branches'] = [n.name.split('/')[-1] for n in beanch_list]
        commit_info['parents'] = [p.hexsha for p in self.commit_handle.parents]
        
        merged = "TRUE" if len(commit_info['parents'])>1 else "FALSE"
        commit_info['merge'] = merged
        commit_info['branches'].remove('HEAD')
        
        try:
            master_check = self.filled_repo.active_branch.name == 'master'
            commit_info['in_main_branch'] = 'True' if master_check else 'False'
        
        #for all older commits, maybe a bit dirty way to use exceptions
        except TypeError as err:
            master_check = detached_name == 'master'
            commit_info['in_main_branch'] = 'True' if master_check else 'False'
        return commit_info
    
    ## @brief Used when parsing the data from git into a file
    #  @note condidate for private method  
    def getAllCommitData(self):
        self.commit_handle = self.filled_repo.head.commit
        original_head = self.commit_handle.hexsha
        original_branch = self.filled_repo.active_branch.name
        self.all_commit_data = []
        while True:
            try:
                old_commit_head = self.filled_repo.commit('HEAD~1')
                self.filled_repo.head.reference = old_commit_head
                self.all_commit_data.append(self.getCommitData(original_branch))
            except git.BadName as exc:
                break 
        
        original_commit_head = self.filled_repo.commit(original_head)
        self.filled_repo.head.reference = original_commit_head

    ## @brief Changes current active branch
    #  @param[in] branch Name of the branch that you want to switch to
    #  @see getBranches() method
    def changeBranch(self,branch):
        if(branch not in self.getBranches()):
            return False
        else:
            self.filled_repo.git.checkout(branch)
            return True

    ## @brief Returns the list of all banches in the repo
    def getBranches(self):
        all_branches = self.filled_repo.remotes.origin.refs
        self.branches = [n.name.split('/')[-1] for n in all_branches]
        return self.branches
    
    ## gitParse
    #  @brief Takes the dict with git info and dumps it into .csv
    #  @param git_info      Dictionary with info
    #  @param csv_name      Filename for output
    def gitParse(self, csv_name='analysis_git.csv'):
        self.getAllCommitData() 
        df = DataFrame(self.all_commit_data)
        df.to_csv(csv_name)

    ## @brief Placeholder method that should be replaced with a nicer call.
    #  @param[in] locked_url Url of password protected repostiory
    #  @param[in] username Either None or username supplied from the method call
    #  @param[in] password Either None or password supplied from the method call
    #  @return new_url Modified url that contains password and username reference 
    def _getPass(self,locked_url,username,password):
        if(username == None):
            username = input("Your username: ")
        if(password == None):
            password = input("Your password: ")
            
        user_pass =  username + ':' + password 
        new_url = "https://" + user_pass + '@' + locked_url.lstrip('https://')
        return new_url

    ## @brief Raises an exception if there is something wrong with the url.
    #  @param[in] remote_url Reporsitory url. 
    def _repoUrlTest(self,remote_url):
        if remote_url == None:
            raise NoUrlSpecified('You need to specify repository URL')
        if (type(remote_url) != str) or (not remote_url.endswith('.git')):
            raise WrongUrlFormat("Wrong URL.\nIN: {}".format(remote_url))

class UrlException(Exception):
    pass
class NoUrlSpecified(UrlException):
    pass
class WrongUrlFormat(UrlException):
    pass


if __name__ == "__main__":
    com_inf = []
    repo_url = 'https://github.com/apache/commons-collections.git'
	# wont work if we try to init what is already existent
    if(os.path.isdir(curr_work_dir)):
        shutil.rmtree(curr_work_dir)
    with GitRepo(curr_work_dir,repo_url) as repo_instance:
        com_inf.append(repo_instance.getCommitData())
        repo_instance.gitParse()
