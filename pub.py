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

    def set_author(self):
        call(['git', 'config', 'user.name', config['name']], cwd=config['pages_dir'])
        call(['git', 'config', 'user.email', config['email']], cwd=config['pages_dir'])

    def commit(self, message):
        message = message or 'automatic update'
        call(['git', 'add', '-A'], cwd=config['pages_dir'])
        call(['git', 'commit', '-m', message], cwd=config['pages_dir'])

    def push(self):
        call(['git', 'push', 'origin', 'gh-pages'], cwd=config['pages_dir'])
        call(['rm', '-rf', config['tmp_dir']])

    def run(self, message=None):
        self.set_author()
        self.commit(message)
        self.push()


class Downloader(object):

    def compose_url(self, repo):
        return 'https://{username}:{password}@github.com/{repo}.git'.format(
            username=config['username'],
            password=config['password'],
            repo=repo
        )

    def compose_command(self, repo, dir, branch=None):
        url = self.compose_url(repo)
        parts = ['git', 'clone']
        if branch:
            parts += ['-b', branch]
        return parts + [url, dir]

    def run(self, repo, dir, branch=None):
        call(self.compose_command(repo, dir, branch))


class Task(object):

    def __init__(self):
        self.downloader = Downloader()
        self.publisher = Publisher()

    def log(self, message):
        sys.stderr.write('[pub] {}\n'.format(message))

    def prepare_tmp_dir(self):
        call(['rm', '-rf', config['tmp_dir']])
        call(['mkdir', config['tmp_dir']])

    def read_definitions(self):
        with open(config['scripts_file']) as f:
            lines = filter(None, f.readlines())
        for line in lines:
            yield filter(None, re.split(r'\s+', line))

    def install(self, requirements):
        call(['pip', 'install', '-r', requirements, '-q'])

    def process(self, script_repo, pages_repo):
        # prepare tmp directory
        self.prepare_tmp_dir()

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

        # install requirements
        requirements = os.path.join(config['tmp_dir'], 'requirements.txt')
        if os.path.exists(requirements):
            self.log('Installing requirements.')
            self.install(requirements)

        try:
            # run script's pubfile.py
            self.log('Calling pubfile.py.')
            call(['python', 'pubfile.py'], cwd=config['tmp_dir'])

            # publish changes
            self.log('Publishing.')
            self.publisher.run()

        except ImportError as e:
            self.log('Missing requirements ({}).'.format(str(e)))
        except Exception as e:
            self.log('Script failed ({}).'.format(str(e)))

    def run(self):
        self.log('Starting.')
        for script_repo, pages_repo in self.read_definitions():
            self.log('Script {} to pages {}.'.format(script_repo, pages_repo))
            self.process(script_repo, pages_repo)
        self.log('Terminating.')


if __name__ == '__main__':
    Task().run()
