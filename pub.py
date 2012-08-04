# -*- coding: utf-8 -*-


import os
import sys
import re
from subprocess import call


config = {
    # tmp directory on Heroku: https://devcenter.heroku.com/articles/read-only-filesystem
    'tmp_dir': os.path.join('.', 'tmp'),
    'pages_dir': os.path.join('.', 'tmp', 'output'),

    # scripts file with definitions of repos
    'scripts_file': os.path.join('.', 'scripts'),

    # GitHub credentials
    'username': os.environ.get('GITHUB_USERNAME'),
    'password': os.environ.get('GITHUB_PASSWORD'),

    # commit author
    'name': os.environ.get('COMMIT_NAME'),
    'email': os.environ.get('COMMIT_EMAIL'),
}


class Publisher(object):

    def _set_author(self):
        call(['git', 'config', 'user.name', config['name']], cwd=config['pages_dir'])
        call(['git', 'config', 'user.email', config['email']], cwd=config['pages_dir'])

    def _commit(self, message):
        message = message or 'automatic update'
        call(['git', 'add', '-A'], cwd=config['pages_dir'])
        call(['git', 'commit', '-m', message], cwd=config['pages_dir'])

    def _push(self):
        call(['git', 'push', 'origin', 'gh-pages'], cwd=config['pages_dir'])
        call(['rm', '-rf', config['tmp_dir']])

    def run(self, message=None):
        self._set_author()
        self._commit(message)
        self._push()


class Downloader(object):

    def _compose_url(self, repo):
        return 'https://{username}:{password}@github.com/{repo}.git'.format(
            username=config['username'],
            password=config['password'],
            repo=repo
        )

    def _compose_command(self, repo, dir, branch=None):
        url = self._compose_url(repo)
        parts = ['git', 'clone']
        if branch:
            parts += ['-b', branch]
        return parts + [url, dir]

    def run(self, repo, dir, branch=None):
        call(self._compose_command(repo, dir, branch))


class Task(object):

    def __init__(self):
        self.downloader = Downloader()
        self.publisher = Publisher()

    def log(self, message):
        sys.stderr.write('[pub] {}\n'.format(message))

    def _prepare_tmp_dir(self):
        call(['rm', '-rf', config['tmp_dir']])
        call(['mkdir', config['tmp_dir']])

    def _read_definitions(self):
        with open(config['scripts_file']) as f:
            lines = f.readlines()
        for line in lines:
            yield re.split(r'\s+', line)

    def _process(self, script_repo, pages_repo):
        # prepare tmp directory
        self._prepare_tmp_dir()

        # download both script and pages
        self.log('Downloading script.')
        self.downloader.run(
            script_repo,
            config['tmp_dir']
        )
        self.log('Downloading pages.')
        self.downloader.run(
            pages_repo,
            config['pages_dir'],
            branch='gh-pages'
        )

        # run script's pubfile.py
        self.log('Calling pubfile.py.')
        call(['python', 'pubfile.py'], cwd=config['tmp_dir'])

        # publish changes
        self.log('Publishing.')
        self.publisher.run()

    def run(self):
        self.log('Starting.')
        for script_repo, pages_repo in self._read_definitions():
            self.log('Script {} to pages {}.'.format(script_repo, pages_repo))
            self._process(script_repo, pages_repo)
        self.log('Terminating.')


if __name__ == '__main__':
    Task().run()
