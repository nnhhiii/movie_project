from django.contrib.auth import logout
from django.shortcuts import render, redirect
from pyexpat.errors import messages
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.forms import LoginForm
from app.models import *
from app.serializers import *


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    @action(detail=False, methods=['get'], url_path='status/(?P<status_type>[^/.]+)')
    def filter_by_status(self, request, status_type=None):
        # Lọc phim theo trạng thái nhận từ URL (now_showing hoặc coming_soon)
        movies = Movie.objects.filter(status=status_type)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class ScreeningViewSet(viewsets.ModelViewSet):
    queryset = Screening.objects.all()
    serializer_class = ScreeningSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        movie_id = self.request.query_params.get('movie_id')
        screening_date = self.request.query_params.get('screening_date')

        if movie_id:
            queryset = queryset.filter(movie=movie_id)
        if screening_date:
            queryset = queryset.filter(screening_date=screening_date)

        return queryset

class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        room_id = self.request.query_params.get('room_id')
        status = self.request.query_params.get('status', 'booked')

        if room_id:
            queryset = queryset.filter(room=room_id, status=status)

        return queryset

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

def index(request):
    return render(request, 'index.html')
def booking(request):
    return render(request, 'ticket-booking.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Kiểm tra thông tin đăng nhập
            try:
                user = User.objects.get(email=email, password=password)
                request.session['current_user_id'] = user.id  # Lưu ID người dùng vào session
                user.is_active = True
                user.save()
                return redirect('http://127.0.0.1:8000/')

            except User.DoesNotExist:
                messages.error(request, "Sai thông tin đăng nhập.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)  # Đăng xuất và xóa session
    return redirect('login')