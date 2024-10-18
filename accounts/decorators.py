from django.shortcuts import redirect

def admin_required(
    function=None,
    redirect_to="/",
):
    """
    Decorator for views that checks that the logged-in user is a superuser,
    redirects to the specified URL if necessary.
    """
    def test_func(user):
        return user.is_active and user.is_superuser

    def wrapper(request, *args, **kwargs):
        if test_func(request.user):
            return function(request, *args, **kwargs) if function else None
        else:
            return redirect(redirect_to)

    return wrapper if function else test_func


def advertiser_required(
    function=None,
    redirect_to="/",
):
    """
    Decorator for views that checks that the logged-in user is an advertiser,
    redirects to the specified URL if necessary.
    """
    def test_func(user):
        return user.is_active and (user.is_advertiser or user.is_superuser)

    def wrapper(request, *args, **kwargs):
        if test_func(request.user):
            return function(request, *args, **kwargs) if function else None
        else:
            return redirect(redirect_to)

    return wrapper if function else test_func


def content_creator_required(
    function=None,
    redirect_to="/",
):
    """
    Decorator for views that checks that the logged-in user is a content creator,
    redirects to the specified URL if necessary.
    """
    def test_func(user):
        return user.is_active and (user.is_content_creator or user.is_superuser)

    def wrapper(request, *args, **kwargs):
        if test_func(request.user):
            return function(request, *args, **kwargs) if function else None
        else:
            return redirect(redirect_to)

    return wrapper if function else test_func
