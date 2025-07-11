from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from user import views as user_view
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),

    path('profile/', user_view.profile, name='user-profile'),
    path('profile/update/', user_view.profile_update, name='user-profile-update'),

    path('user/', include('user.urls', namespace='user')),

    # path('', RedirectView.as_view(url='/user/login/', permanent=False)),
     path('', user_view.landing_page, name='landing_page'),
    # path('', RedirectView.as_view(url='/dashboard/register', permanent=False)),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
