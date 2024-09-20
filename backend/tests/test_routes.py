from http import HTTPStatus
from django.urls import reverse


def test_home_avaiblity_for_anonymous_user(client):
    url = reverse('')