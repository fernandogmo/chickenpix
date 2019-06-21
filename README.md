# Chickenpix :chicken: :camera:
Photosharing without social media.

## Motivation :muscle:
In order to share pictures of events with others, we often have to sacrifice some privacy. Even then, it's not possible to download all the pictures from a specific event - on Facebook, you have to save each picture indiviudally. On Instagram, you can't even download a picture. You have to take a screenshot. We aim to solve that by providing a way to upload pictures privately and share them with your friends. We use passwordless login so no sensitive information other than the photos will be shared with us.

## Requirements :white_check_mark:
- Python (3.6+)
- Django (2.0+)
- Django Rest Framework + AuthToken (3.6+)
- pipenv 

## Tech/framework used :floppy_disk:
- [Python](https://docs.python.org/3/)
- [Django](https://docs.djangoproject.com/en/2.2/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [drfpasswordless](https://github.com/aaronn/django-rest-framework-passwordless)
- [requests](https://2.python-requests.org/en/master/)
- [pillow](https://pillow.readthedocs.io/en/stable/)
- [sqlite](https://sqlite.org/docs.html)
- [python-decouple](https://pypi.org/project/python-decouple/)

## Installation :open_file_folder:
1) Install django
```
apt-get install django
```
2) Install pipenv
```
pip3 install pipenv
```
3) Clone our repo
```
git clone git@github.com:fgonza52/pixguise.git
```
4) Go into your project directory and enter the pipenv shell
```
pipenv shell
```
5) Install required libraries using pipenv
```
pipenv install --dev
```
6) Make django database migrations
```
python3 manage.py makemigrations
python3 manage.py migrate
```
6) Create .env file - look at `.env.example` file for inspiration - and insert the necessary variables. 
7) Run server using django
```
python3 manage.py runserver
```
The default server will be run on `127.0.0.1:8000`/`localhost:8000`. To use another IP address, just add it after `runserver`, i.e.:
```
python3 manage.py runserver 0.0.0.0:8000
```
7) Using your preferred browser, go to the IP you are running your server on.

## Contribute :computer:
We welcome any contributions to our project - fork our repository and submit a Pull Request if you feel you've made any improvements.

## License :scroll:
[MIT](https://github.com/fgonza52/pixguise/blob/master/LICENSE) &#169; [Fernando Gonzalez-Morales](https://fernando.ai/) [Allison Weiner](https://jozsa.github.io)
