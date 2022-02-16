import datetime


def year(request):
    return {
        'year': datetime.date.today().year
    }
