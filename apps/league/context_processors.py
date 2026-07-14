from django.conf import settings


def site_info(request):
    """
    Context processor: expone datos globales del sitio (footer, liga)
    para que estén disponibles en TODOS los templates sin necesidad de
    repetirlos en cada vista.
    """
    return {
        'site_developers': getattr(settings, 'SITE_DEVELOPERS', []),
        'site_course_name': getattr(settings, 'SITE_COURSE_NAME', ''),
        'site_year': getattr(settings, 'SITE_YEAR', ''),
        'league_name': getattr(settings, 'LEAGUE_NAME', 'Junior Baseball League'),
    }
