import time
import grpc
import exchange_pb2
import exchange_pb2_grpc

def run():
    # Menargetkan Server B menggunakan nama alias kontainer jaringan Docker
    channel = grpc.insecure_channel('receiver-container:50051')
    stub = exchange_pb2_grpc.ExchangeServiceStub(channel)

    print("=== SERVER A: ANTARMUKA ALIRAN DATA PROTOC ===")
    print("Ketik 'exit' pada bagian NIM kapan saja untuk menutup aliran data.\n")

    while True:
        input_id = input("Masukkan NIM Mahasiswa: ")
        if input_id.strip().lower() == 'exit':
            print("\n[Server A] Menutup aliran koneksi. Sampai jumpa!")
            break

        input_name = input("Masukkan Nama Mahasiswa: ")
        start_time = time.time_ns()

        # Instansiasi objek kelas kompilasi Protobuf
        student_data = exchange_pb2.StudentRequest(
            student_id=input_id,
            student_name=input_name,
            sent_timestamp_ns=start_time
        )

        payload_size_bytes = student_data.ByteSize()
        print(f" -> Serialisasi Lokal: {payload_size_bytes} bytes")
        print(" -> Mengirimkan...")

        try:
            response = stub.SendData(student_data)
            if response.status:
                print(" -> Ack (Konfirmasi) diterima dari Penerima.\n")
        except grpc.RpcError as e:
            print(f" -> [ERROR] Koneksi gagal: {e}\n")
            break

if __name__ == '__main__':
    run()