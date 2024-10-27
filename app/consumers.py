# app/consumers.py
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import transaction

from app.models import Seat


class SeatBookingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Lấy `movie_id` từ URL để tạo group cho mỗi bộ phim
        self.movie_id = self.scope['url_route']['kwargs']['movie_id']
        self.room_group_name = f"movie_{self.movie_id}"

        # Tham gia vào group dựa trên movie_id
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Chấp nhận kết nối WebSocket
        await self.accept()

    async def disconnect(self, close_code):
        # Rời khỏi group khi ngắt kết nối
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        seat_number = text_data_json['seat_number']
        action = text_data_json['action']
        user_id = text_data_json['user_id']

        try:
            # Bắt đầu transaction
            async with transaction.atomic():
                seat = await database_sync_to_async(Seat.objects.get)(seat_number=seat_number)

                if action == "booked":
                    if seat.status == 'available':
                        seat.status = 'booked'
                        await database_sync_to_async(seat.save)()
                        # Thông báo thành công
                        await self.send(text_data=json.dumps({
                            'status': 'success',
                            'message': f'Seat {seat_number} has been booked.'
                        }))
                    else:
                        # Xử lý trường hợp ghế đã được đặt
                        await self.send(text_data=json.dumps({
                            'status': 'error',
                            'message': f'Seat {seat_number} is already booked.'
                        }))
                elif action == "release":
                    if seat.status == 'booked':
                        seat.status = 'available'
                        await database_sync_to_async(seat.save)()
                        # Thông báo thành công
                        await self.send(text_data=json.dumps({
                            'status': 'success',
                            'message': f'Seat {seat_number} has been released.'
                        }))
                    else:
                        # Xử lý trường hợp ghế không thể hủy
                        await self.send(text_data=json.dumps({
                            'status': 'error',
                            'message': f'Seat {seat_number} cannot be released because it is not booked.'
                        }))

            # Gửi dữ liệu đến group (phát cho các client khác)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_seat_status',
                    'seat_number': seat_number,
                    'action': action,
                    'user_id': user_id,
                }
            )
        except Exception as e:
            # Xử lý ngoại lệ
            print(f"Error: {e}")
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': 'An error occurred while processing your request.'
            }))

    async def update_seat_status(self, event):
        # Nhận thông điệp từ group và gửi tới WebSocket client
        seat_number = event['seat_number']
        action = event['action']
        user_id = event['user_id']

        # Gửi dữ liệu tới WebSocket client
        await self.send(text_data=json.dumps({
            'seat_number': seat_number,
            'action': action,
            'user_id': user_id,
        }))
