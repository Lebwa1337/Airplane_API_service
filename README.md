# Airplane_API_service
My first own project by using Django REST

### Introduction
This API was created to help tracking flights, and buying tickets,to travel all over the world

### Project Support Features
* Users can signup and login to their accounts
* Project uses JWT token for authentication
* Supports Docker
* Postgres database
* Created tickets already comes with order
* Pagination
* Swagger and Redoc documentation to see all the endpoints
* Filtering by using query parameters
* Custom permissions
### Installation Guide
* Clone this repository [here](https://github.com/Lebwa1337/Airplane_API_service/).
* The develop branch is the most stable branch at any given time, ensure you're working from it.
* Run `pip install -r requirements.txt` to install all dependencies
* Create an .env file in your project root folder and add your variables. See .env_sample for assistance.
* Run server locally or use docker to run it
### Usage
If you wanna launch API from IDE:
* Make sure you do all in installation guide
* Run `python manage.py runserver`
Also you can run API by using docker:
* First you need to have Docker desktop on your PC
* Run `docker-compose up --build`
For admin permissions you need to create superuser by running `python manage.py createsuperuser`. <br />
In case of docker firstly you need to get container name, run `docker ps`
then open shell in your terminal, use: `docker exec -it {your container name} sh` and then run `python manage.py createsuperuser`

### API Endpoints
Here some crucial endpoints:

| HTTP Verbs | Endpoints               | Action                                                                   |
| --- |-------------------------|--------------------------------------------------------------------------|
| POST | /api/user/register      | To register your account                                                 |
| POST | /api/user/token         | To get your access token                                                 |
| POST | /api/user/token/refresh | To refresh your access token                                             |
| GET | /api/service            | To get all service endpoint                                              |
| GET | /api/doc/swagger        | To see swagger documentation<br/>and all possible endpoints with methods |

### Technologies Used
* [Django](https://www.djangoproject.com)
* [Django REST framework](https://www.django-rest-framework.org) 
* [Docker](https://www.docker.com)
* [Docker hub](https://hub.docker.com)

### Database structure
![img.png](demo_files/exported_from_idea.drawio.png)

