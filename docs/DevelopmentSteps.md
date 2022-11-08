install
	Chrome
	https://code.visualstudio.com/
		Extensions
			Pylance
			Atom One Dark Theme
			Auto Rename Tag		
			Prettier
			Azure Tools
	https://git-scm.com/download
		From Git Bash
			git config --global user.name "xs2sachin"
			git config --global user.email "xs2sachin@gmail.com"
	https://www.python.org/downloads/
		From Command Prompt
			pip install virtualenv
			pip install django
			pip install cookiecutter
			pip install pre-commit
				pre-commit install
			pip install -U ggshield
				ggshield auth login
	https://docs.docker.com/get-docker/#supported-platforms

	Termimal
		Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
		virtualenv venv
		.\venv\Scripts\activate
		create production_settings
		create logs folder

	

	irm get.scoop.sh -outfile 'install.ps1'
	.\install.ps1 -RunAsAdmin 

	scoop install sudo

	Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

	choco install mkcert
	 mkcert onsmarttrack.com '*.onsmarttrack.com' localhost 127.0.0.1 ::1

	
	node.js
	
	https://docs.docker.com/get-docker/#supported-platforms
	https://visualstudio.microsoft.com/visual-cpp-build-tools/  #Microsoft C++ build tools
	https://visualstudio.microsoft.com/downloads/
	https://dev.mysql.com/downloads/installer/
	https://dev.mysql.com/downloads/windows/visualstudio/
	https://sourceforge.net/projects/mkcert.mirror/
	https://devcenter.heroku.com/articles/getting-started-with-python#set-up
	visual studio code
	python
	SSMS

Create new Project Folder
Open in CMD

# https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html

git init

cookiecutter gh:cookiecutter/cookiecutter-django

pip install -r requirements/local.txt

createdb --username=Sachin ontrack # create from pgamdin

docker-compose -f local.yml build
docker-compose -f local.yml up
docker-compose -f local.yml run --rm django python manage.py migrate
docker-compose -f local.yml run --rm django python manage.py createsuperuser

docker-compose -f local.yml run --rm django python dumpdata > db.json

docker logs ontrack_local_celeryworker
docker top ontrack_local_celeryworker

mkcert onsmarttrack.com localhost

python manage.py inspectdb > models.py
python manage.py makemigrations
python manage.py migrate --fake-initial

https://coderwall.com/p/mvsoyg/django-dumpdata-and-loaddata
	python manage.py dumpdata > db.json
	python manage.py dumpdata admin > admin.json
	python manage.py dumpdata admin.logentry > logentry.json
	python manage.py dumpdata auth.user > user.json
	python manage.py dumpdata --exclude auth.permission > db.json
	python manage.py dumpdata auth.user --indent 2 > user.json

	python manage.py loaddata user.json

	Restore in fresh database 
	py manage.py dumpdata --exclude auth.permission --exclude contenttypes > db.json
	./manage.py loaddata db.json


docker-compose -f local.yml run --rm django pytest
$ docker-compose -f local.yml run --rm django coverage run -m pytest
$ docker-compose -f local.yml run --rm django coverage report


https://kubernetes.io/docs/tasks/tools

Invoke-WebRequest https://github.com/digitalocean/doctl/releases/download/v1.81.0/doctl-1.81.0-windows-amd64.zip -OutFile ~\doctl-1.81.0-windows-amd64.zip
Expand-Archive -Path ~\doctl-1.81.0-windows-amd64.zip
New-Item -ItemType Directory $env:ProgramFiles\doctl\
Move-Item -Path ~\doctl-1.81.0-windows-amd64\doctl.exe -Destination $env:ProgramFiles\doctl\
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path",
    [EnvironmentVariableTarget]::Machine) + ";$env:ProgramFiles\doctl\",
    [EnvironmentVariableTarget]::Machine)
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")

doctl auth init --context <NAME>
doctl auth list
doctl auth switch --context <NAME>
doctl account get
kubectl --kubeconfig=/<pathtodirectory>/onsmarttrack-kubeconfig.yaml get nodes

doctl compute droplet create --region tor1 --image ubuntu-18-04-x64 --size s-1vcpu-1gb <DROPLET-NAME>


pre-commit run --all-files

git update-index --skip-worktree .envs/.local/.postgre