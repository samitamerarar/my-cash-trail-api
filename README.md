# my-cash-trail

# Start the project

```
docker-compose down
docker-compose build
docker-compose up

docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py test && flake8"
```

# DEV

## To make migrations

```
docker-compose run --rm app sh -c "python manage.py makemigrations"
```

## Start a new app

1. Run:

```
docker-compose run --rm app sh -c "python manage.py startapp nameoftheapp"
```

2. in app.settings.py add to INSTALLED_APPS = ['nameoftheapp']

### Add API to the new app

1. Inside the new app
2. create a serializers.py
3. create a views.py and add the Serializer
4. create urls.py add add the View to urlpatterns
5. in parent app (app), add in app.urls.py urlpatterns for nameoftheapp.urls

## Delete Table

```
manage.py migrate --fake <appname> zero
rm -rf migrations
manage.py makemigrations <appname>
manage.py migrate --fake <appname>

This will ...

pretend to rollback all of your migrations without touching the actual tables in the app
remove your existing migration scripts for the app
create a new initial migration for the app
fake a migration to the initial migration for the app
```
