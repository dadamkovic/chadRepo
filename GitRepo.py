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

curr_work_dir = os.path.join(os.getcwd(), 'tmpRepo')

## Class that provides all he neccessary funcitonality associated with git repos
#
#

class GitRepo():
    
    ## creates empty repository, pulled repositories will be stored here
    def __init__(self,work_dir=curr_work_dir):
        self.work_dir = work_dir
    
    ## @brief Downloads the repo contents
	#  @param remote_url Reporsitory url (by default this is None)
	#  @param username Needed in case of pass protected repo
    #  @param password Needed in case of pass protected repo
    #  @returns True if repo pulled successfuly, False otherwise
    #
    #  The method will check if the repostitory is in valid format and create workRepo
    #  with contents of the user specified directory. If the repo is password
    #  protected it will request user input (password can also be specified as input arg).
    def pullRepoContents(self,remote_url=None,username=None,password=None):
        try:
			#testing the url for validity
            self._repoUrlTest(remote_url)     
        except UrlException as exc:
            print(exc)
            return False
        self.repo_url = remote_url

        try:
            filled_repo = git.Repo.clone_from(self.repo_url,self.work_dir)

		#if we enter exception we have tried to pull private repo or supplied bad path        
        except git.cmd.CommandError:    
			                     
            print("ERROR directory " + self.repo_url + " exists and not empty/pass protected git")
			#add username and pass to the remote url
            unlocked_url = self._getPass(self.repo_url,username,password)  
            print("Trying to unlock")  
            filled_repo = git.Repo.clone_from(unlocked_url,self.work_dir)
                                             
        self.filled_repo = filled_repo      #save the created repo information
        return True
    
    ## @brief Returns the dictionary with all the neccessary information
    #  @note  Merge allways returns empty list because I don't know what else to do there 
    def getCommitData(self):    
        commit_info = {}
        self.commit_handle = self.filled_repo.head.commit
        time_struct = time.gmtime()
        date_author = time.strftime("%Y-%m-%dT:%H:%M:%SZ",time_struct)
        time_struct = time.gmtime(self.commit_handle.committed_date)
        date_commiter = time.strftime("%Y-%m-%dT:%H:%M:%SZ",time_struct)
        
        
        self.commit_handle = self.filled_repo.head.commit
        commit_info['project_id'] = self.repo_url.split('/')[-1].rstrip('.git')
        commit_info['hash'] = self.commit_handle.hexsha
        commit_info['message'] = self.commit_handle.message
        commit_info['author'] = self.commit_handle.author.name
        commit_info['author_date'] = date_author
        commit_info['author_timezone'] = self.commit_handle.author_tz_offset/3600
        commit_info['commiter'] = self.commit_handle.committer.name
        commit_info['commiter_date'] = date_commiter
        commit_info['commiter_timezone'] = self.commit_handle.committer_tz_offset/3600
        commit_info['branches'] = [n.name.split('/')[-1] for n in self.filled_repo.remotes.origin.refs]
        commit_info['in_main_branch'] = 'True' if self.filled_repo.active_branch.name == 'master' else 'False'
        commit_info['parents'] = [p.hexsha for p in self.commit_handle.parents]
        commit_info['merge'] = "TRUE" if len(commit_info['parents'])>1 else "FALSE"
        commit_info['branches'].remove('HEAD')
        return commit_info
    
    ## @param[in] branch Name of the branch that you want to switch to
    #  @see getBranches() method
    def changeBranch(self,branch):
        if(branch not in self.getBranches()):
            return False
        else:
            self.filled_repo.git.checkout(branch)
            return True
    
    ## Returns the list of all banches in the repo
    def getBranches(self):
        self.branches = [n.name.split('/')[-1] for n in self.filled_repo.remotes.origin.refs]
        return self.branches
    
    ## @param[in] locked_url Url of password protected repostiory
    #  @param[in] username Either None or username supplied from the method call
    #  @param[in] password Either None or password supplied from the method call
    #  @return new_url Modified url that contains password and username reference
    #  Placeholder method that should be replaced with a nicer call
    def _getPass(self,locked_url,username,password):
        if(username == None):
            username = input("Your username: ")
        if(password == None):
            password = input("Your password: ")
        
        new_url = "https://" + username + ':' + password + '@' + locked_url.lstrip('https://')
        return new_url
        
    ## @param[in] remote_url Reporsitory url, username and pass info will be added to this
    #  Raises an exception if there is something wrong with the url
    def _repoUrlTest(self,remote_url):
        if remote_url == None:
            raise NoUrlSpecified('You need to specify repository URL')
        if (type(remote_url) != str) or (not remote_url.endswith('.git')):    
            raise WrongUrlFormat("Wrong url format.\nInput: {}".format(remote_url))
          
class UrlException(Exception):
    pass
class NoUrlSpecified(UrlException):
    pass
class WrongUrlFormat(UrlException):
    pass


if __name__ == "__main__":
    com_inf = []
	#wont work if we try to init what is already existent
    if(os.path.isdir(curr_work_dir)):      
        shutil.rmtree(curr_work_dir)
    repo_instance =  GitRepo(curr_work_dir)
    repo_instance.pullRepoContents('https://github.com/apache/commons-cli.git')   
    com_inf.append(repo_instance.getCommitData())
    if repo_instance.changeBranch(com_inf[0]['branches'][0]):
        print("Success!")
        com_inf.append(repo_instance.getCommitData())
        
