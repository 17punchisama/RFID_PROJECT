import csv
import paho.mqtt.client as mqtt
from datetime import datetime
import os

# ตั้งค่าชื่อไฟล์ CSV
csv_file = "sensor_data.csv"

# ฟังก์ชันสำหรับบันทึกข้อมูลลงในไฟล์ CSV
def write_to_csv(data):
    # เปิดไฟล์ในโหมด append หรือสร้างใหม่ถ้าไม่มีไฟล์
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # ถ้าไฟล์ยังไม่มี header ก็ใส่ header ลงไปก่อน
        if not file_exists:
            writer.writerow(["Timestamp", "Temperature", "Humidity", "LDR Value"])  # ปรับชื่อคอลัมน์ตามข้อมูลของเซนเซอร์

        # เขียนข้อมูลลงใน CSV
        writer.writerow(data)

def on_message(client, userdata, msg):
    # รับข้อมูลจาก MQTT แล้วแปลงเป็น string
    sensor_data = msg.payload.decode('utf-8')
    print(f"Received message: {sensor_data}")

    # บันทึกข้อมูลพร้อมกับ timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Saving to CSV: {timestamp}, {sensor_data}")

    # แยกข้อมูลจากข้อความ JSON
    import json
    try:
        data_dict = json.loads(sensor_data)
        temperature = data_dict.get("temperature")
        humidity = data_dict.get("humidity")
        ldr_value = data_dict.get("ldrValue")
        write_to_csv([timestamp, temperature, humidity, ldr_value])
    except json.JSONDecodeError:
        print("Error decoding JSON")

# ฟังก์ชัน callback เมื่อเชื่อมต่อสำเร็จ
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # ระบุ topic ที่ต้องการ subscribe
    client.subscribe("esl/zero2hero")

# ตั้งค่าการเชื่อมต่อ MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# ตั้งค่าการเชื่อมต่อกับ broker
client.connect("broker.hivemq.com", 1883, 60)

# เริ่ม loop เพื่อรับข้อมูลจาก broker
client.loop_forever()
