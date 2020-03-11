
import requests
from itertools import count


## Class for SonarQube web api
# public api includes:
#   - issues
#   - projects
#   - delete_project
#   - ready
class API:
    ##
    # @param url Url of the running SonarQube instance
    # @param auth Authorisation for the SonarQube instance
    def __init__(self, url='http://127.0.0.1:9000', auth=('admin', 'admin')):
        self.url = url
        self.auth = auth
        self.ps = 100

    @property
    def pagesize(self):
        return min(max(self.ps, 10), 500)

    @pagesize.setter
    def pagesize(self, val):
        if val < 10 or val > 500:
            raise ValueError('pagesize must be between 10 and 500, inclusive')
        self.ps = val

    def get(self, path, key, parser, *, params=None):
        pagesize = self.pagesize
        done = 0
        params = params or {}
        for page in count(1):
            res = requests.get(
                f'{self.url}/api/{path}',
                params={**params, 'ps': pagesize, 'p': page},
                auth=self.auth
            )
            res = res.json()
            if 'errors' in res:
                raise Exception(res['errors'])
            yield from map(parser, res[key])
            done += pagesize
            if done >= res['paging']['total']:
                return

    ## Delete existing project
    # @param project_key Project to delete
    # @returns whether the response was ok
    def delete_project(self, project_key):
        return requests.post(
            f'{self.url}/api/projects/delete',
            params={'project': project_key},
            auth=self.auth
        ).ok

    ## ready SonarQube is up and ready to use
    # @returns True if the SonarQube instance is ready, False otherwise
    def ready(self):
        try:
            res = requests.post(f'{self.url}/api/system/status', auth=self.auth).json()
            return res['status'] == 'UP'
        except Exception:
            pass
        return False

    ## search project keys for all analysed projects
    # @returns Generator of project keys as string
    # @param auth Authorisation for the SonarQube instance
    def projects(self):
        yield from self.get('projects/search', 'components', lambda x: x['key'])

    ## search issues for projects
    # @param project The project key for which issues are wanted
    # @returns Generator of issues
    def issues(self, *, project=None):
        params = {}
        if project is not None:
            params['componentKeys'] = project
        yield from self.get('issues/search', 'issues', lambda x: x, params=params)


if __name__ == '__main__':
    api = API()
    print(list(api.projects()))

