
import requests
from itertools import count


class API:
    def __init__(self):
        self.auth = 'admin', 'admin'
        self.url = 'http://127.0.0.1:9000'

    def get(self, path, key, parser):
        pagesize = 100
        done = 0
        for page in count(1):
            res = requests.get(
                f'{self.url}/api/{path}',
                params={'ps': pagesize, 'p': page},
                auth=self.auth
            )
            res = res.json()
            if 'errors' in res:
                raise Exception(res['errors'])
            yield from map(parser, res[key])
            done += pagesize
            if done >= res['paging']['total']:
                return

    def delete_project(self, project_key):
        return requests.post(
            f'{self.url}/api/projects/delete',
            params={'project': project_key},
            auth=self.auth
        )

    def projects(self):
        yield from self.get('projects/search', 'components', lambda x: x['key'])

    def issues(self, **params):
        yield from self.get('issues/search', 'issues', lambda x: x)


if __name__ == '__main__':
    api = API()
    print('projects:', list(api.projects()))
    print(len(list(api.issues())), 'issues')

