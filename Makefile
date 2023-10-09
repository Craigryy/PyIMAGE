.PHONY: run migrate collectstatic test

# Run the development server
run:
	cd pyIMAGE && python manage.py runserver 

# Run database migrations
migrate:
	cd pyIMAGE && python manage.py makemigrations 
	cd pyIMAGE && python manage.py migrate

	 
# Collect static files
collectstatic:
	cd pyIMAGE && python manage.py collectstatic --noinput

# Run tests
test:
	cd pyIMAGE && python manage.py test
