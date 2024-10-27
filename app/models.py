from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class Genre(models.Model):
    genre_name = models.CharField(max_length=255)

class Movie(models.Model):
    title = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    duration = models.IntegerField()  # in minutes
    description = models.TextField()
    image_ava = models.TextField(default='https://cinema.momocdn.net/img/76909001427055070-rkbse0ifgemkVtJKm7qWKy0vqj5.jpg')
    image_cover = models.TextField(default='https://cinema.momocdn.net/img/76909001873562492-AaYdXkEqExgG66p55J677Qnagpf.jpg')
    trailer = models.TextField(default='https://www.youtube.com/embed/0HY6QFlBzUY?autoplay=1')
    status = models.CharField(max_length=20, default='now_showing')

    def __str__(self):
        return self.title


class Room(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name


class Screening(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    screening_time = models.DateTimeField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.movie.title} at {self.screening_time}"


class Seat(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)  # e.g., A1, B2, etc.
    status = models.CharField(max_length=50, default='available')  # available, reserved, booked

    def __str__(self):
        return f"{self.seat_number} in {self.room.name}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user.username} for {self.seat.seat_number} in {self.screening.room.name}"
