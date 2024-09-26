from concurrent import futures
import grpc
from proto import auth_service_pb2
from proto import auth_service_pb2_grpc
from models import User
from server.database_service.python_database_service.connection import get_bd


class AuthServiceGRPC(auth_service_pb2_grpc.AuthServiceServicer):
    def GetUsers(self, request, context):
        db = next(get_bd())
        try:
            users = db.query(User).all()  # Получаем пользователей
            users_list = [{
                'name': u.user_name,
                'created_at': u.created_at.isoformat(),
                "reqToken": u.reqToken,
                "user_id": u.user_id,
                "admin": u.admin
            } for u in users]

            # Формируем ответ
            user_messages = [
                auth_service_pb2.User(
                    name=u['name']
                )
                for u in users_list
            ]

            return auth_service_pb2.UserList(users=user_messages)

        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_service_pb2.UserList()  # Пустой ответ в случае ошибки


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_service_pb2_grpc.add_AuthServiceServicer_to_server(AuthServiceGRPC(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server is running on port 50051...")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
