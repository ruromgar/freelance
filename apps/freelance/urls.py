from django.urls import path

from apps.freelance.views import close_year
from apps.freelance.views import index
from apps.freelance.views import quarterly_summary
from apps.freelance.views import yearly_summary

app_name = "freelance"

urlpatterns = [
    path("", index, name="index"),
    path("<int:year>/", yearly_summary, name="yearly_summary"),
    path("<int:year>/close/", close_year, name="close_year"),
    path("<int:year>/<int:quarter>/", quarterly_summary, name="quarterly_summary"),
]
