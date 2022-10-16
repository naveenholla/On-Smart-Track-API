-Softwares    
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
    https://www.postgresql.org/download/windows/

- Open Powershell
- Run Following commands
    virtualenv venv

    .\venv\Scripts\activate

    python.exe -m pip install --upgrade pip
    pip install django
	pip install cookiecutter

    git init

	pip install pre-commit
	pre-commit install	

	pip install -U ggshield
	ggshield auth login	

    cookiecutter gh:cookiecutter/cookiecutter-django
        project_name [My Awesome Project]:              On Smart Track
        project_slug [on_smart_project_api]:            ontrack
        description [Behold My Awesome Project!]:       A fully featured financial tracker for personal finance and stock market api | On Smart Track API
        author_name [Daniel Roy Greenfeld]:             Sachin Gupta
        domain_name [example.com]: onsmarttrack.com
        email [sachin-gupta@example.com]:               sachin@onsmarttrack.com
        version [0.1.0]:
        Select open_source_license:
        1 - MIT
        2 - BSD
        3 - GPLv3
        4 - Apache Software License 2.0
        5 - Not open source
        Choose from 1, 2, 3, 4, 5 [1]:                  1
        timezone [UTC]:
        windows [n]:                                    y
        use_pycharm [n]:
        use_docker [n]:
        Select postgresql_version:
        1 - 14
        2 - 13
        3 - 12
        4 - 11
        5 - 10
        Choose from 1, 2, 3, 4, 5 [1]:
        Select cloud_provider:
        1 - AWS
        2 - GCP
        3 - None
        Choose from 1, 2, 3 [1]:                        1
        Select mail_service:
        1 - Mailgun
        2 - Amazon SES
        3 - Mailjet
        4 - Mandrill
        5 - Postmark
        6 - Sendgrid
        7 - SendinBlue
        8 - SparkPost
        9 - Other SMTP
        Choose from 1, 2, 3, 4, 5, 6, 7, 8, 9 [1]:      6
        use_async [n]:                                  y
        use_drf [n]:                                    y
        Select frontend_pipeline:
        1 - None
        2 - Django Compressor
        3 - Gulp
        Choose from 1, 2, 3 [1]:                        2
        use_celery [n]:                                 n
        use_mailhog [n]:                                y
        use_sentry [n]:                                 y
        use_whitenoise [n]:                             y
        use_heroku [n]:                                 y
        Select ci_tool:
        1 - None
        2 - Travis
        3 - Gitlab
        4 - Github
        Choose from 1, 2, 3, 4 [1]:                     4
        keep_local_envs_in_vcs [y]:                     y
        debug [n]:                                      y
        [SUCCESS]: Project initialized, keep up the good work!

- pip install -r requirements/local.txt
- update database details
    git update-index --skip-worktree .envs/.local/.postgre

python manage.py makemigrations
