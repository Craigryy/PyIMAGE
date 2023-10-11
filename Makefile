.PHONY: run migrate collectstatic test


ifeq ($(shell uname), Linux)
    # This is a Linux system
    BROWSER := xdg-open
else
    # This is not a Linux system (e.g., macOS, Windows)
    BROWSER := open
endif


# Flake8 linting
py-flake: ## Run Flake8 linter
	flake8 script

# Autopep8 formatting
py-auto: ## Run autopep8 formatter
	autopep8 -r script --in-place

# Stop containers
stop: ## Stop the Docker containers
	$(DOCKER_COMPOSE) stop

# Teardown app
teardown: ## Stop and remove the Docker containers and associated volumes
	$(DOCKER_COMPOSE) down -v
	
# Start Docker app
start: ## Start the Docker app
	$(DOCKER_COMPOSE) up 

start-detach: ## Start the Docker app
	$(DOCKER_COMPOSE) up -d

# Build Docker containers
build: ## Build Docker containers
	$(DOCKER_COMPOSE) build

# Local Development server
run: # Start the Django development server using Postgres
	poetry run python pyIMAGE/manage.py makemigrations
	poetry run python pyIMAGE/manage.py migrate
	poetry run python pyIMAGE/manage.py runserver
 
# Collect static files
collectstatic:
	cd pyIMAGE && python manage.py collectstatic --noinput

# Run tests
test:
	cd pyIMAGE && python manage.py test
