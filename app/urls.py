from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views
from .serializers import MovieSerializer
from .views import login_view, logout_view, MovieViewSet

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'movies', views.MovieViewSet)
router.register(r'rooms', views.RoomViewSet)
router.register(r'screenings', views.ScreeningViewSet)
router.register(r'seats', views.SeatViewSet)
router.register(r'bookings', views.BookingViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.index, name='index'),
    path('booking', views.booking, name='booking'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout')
]


