import time
from concurrent import futures
import grpc
import exchange_pb2
import exchange_pb2_grpc

class StudentDataServer(exchange_pb2_grpc.ExchangeServiceServicer):
    def SendData(self, request, context):
        arrival_time = time.time_ns()

        # Menghitung metrik latensi satu arah (one-way latency)
        transmission_time_ms = (arrival_time - request.sent_timestamp_ns) / 1_000_000
        data_size = request.ByteSize()

        print("\n📥 === TRANSAKSI PROTOBUF MASUK ===")
        print(f"NIM Mahasiswa    : {request.student_id}")
        print(f"Nama Mahasiswa   : {request.student_name}")
        print(f"Ukuran Payload   : {data_size} bytes")
        print(f"Waktu Transmisi  : {transmission_time_ms:.4f} ms")
        print("========================================")

        return exchange_pb2.StudentResponse(status=True)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    exchange_pb2_grpc.add_ExchangeServiceServicer_to_server(StudentDataServer(), server)
    server.add_insecure_port('[::]:50051')
    print("[Server B] Berjalan di port 50051... Menunggu kiriman data mahasiswa.")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()