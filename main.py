import numpy
import argparse
import cv2
import face_recognition
import os
import mysql.connector
def training(path):
  known_encodings = []
  known_names = []
  if path.endswith("/"):
    for images in os.listdir(path):
      if images.endswith(".jpeg"or".jpg"):
        filter_image = face_recognition.load_image_file(path+images)
        filter_image_encoding = face_recognition.face_encodings(filter_image)[0]
        known_encodings.append(filter_image_encoding)
        known_names.append(images.split(".")[0])
  else:
      for images in os.listdir(path):
        if images.endswith(".jpeg"or".jpg"):
          filter_image = face_recognition.load_image_file(path+"/"+images)
          filter_image_encoding = face_recognition.face_encodings(filter_image)[0]
          known_encodings.append(filter_image_encoding)
          known_names.append(images.split(".")[0])


  return known_encodings,known_names
def capture_image():

  cam = cv2.VideoCapture(0)

  cv2.namedWindow("test")
  img_counter = 0

  while True:
      ret, frame = cam.read()
      if not ret:
          print("failed to grab frame")
          break
      cv2.imshow("test", frame)

      k = cv2.waitKey(1)
      if k%256 == 27:
          # ESC pressed
          print("Escape hit, closing...")
          break
      elif k%256 == 32:
          # SPACE pressed
          img_name = "test_{}.png".format(img_counter)
          cv2.imwrite(img_name, frame)
          print("{} written!".format(img_name))
          img_counter += 1

  cam.release()

  cv2.destroyAllWindows()
  return img_counter

def prediction(file_name,known_encodings,known_names):
  unknown_images = face_recognition.load_image_file(file_name)
  unknown_image_encoding = face_recognition.face_encodings(unknown_images)[0]
  matches = face_recognition.compare_faces(known_encodings,unknown_image_encoding)
  if True in matches:
    match_index = matches.index(True)
    name = known_names[match_index]
  else:
    name="Unknown"
  return name
def update_attendance(hostname,username,password,database_name,predicted_name):
    mydb = mysql.connector.connect(host=hostname,user=username,password=password,database = database_name,auth_plugin='mysql_native_password')
    mycursor = mydb.cursor(buffered=True)
    query = "Select attendance from attendance where name = %s"
    name = (predicted_name,)
    mycursor.execute(query,name)
    row = mycursor.fetchall()
    attendance = row[0][0]
    attendance+=1
    values = (attendance,predicted_name)
    
    query = "Update attendance set attendance= %s where name = %s"
    mycursor.execute(query,values)
    mydb.commit()
    mycursor.close()
    print(predicted_name+" your attendance has been updated")



def calculate_pay(hostname,username,password,dbname,predicted_name):
  connect = mysql.connector.connect(host=hostname,user = username,password = password, database= dbname,auth_plugin='mysql_native_password')
  cursor = connect.cursor(buffered=True)
  query = "Select base_pay,attendance from attendance where name = %s"
  name = (predicted_name,)
  cursor.execute(query,name)
  row = cursor.fetchall()
  base_pay = row[0][0]
  attendance = row[0][1]
  cursor.close()
  return (base_pay*attendance)

def Main():
  parser=  argparse.ArgumentParser()
  parser.add_argument("-calculate","--calculate",help = 'Calculate the pay of the person',action="store_true")
  parser.add_argument("-attendance","--attendance",help = 'To mark the attendance of the person',action = "store_true")
  args = parser.parse_args()

  if args.attendance:
    count = capture_image()
    known_encodings,known_names= training(r"C:\Users\Nitpreet.Nitpreet\Desktop\BEA_Final\Dataset")
    name = prediction(r'C:\Users\Nitpreet.Nitpreet\Desktop\BEA_Final\venv\test_'+str(count-1)+'.png',known_encodings= known_encodings,known_names=known_names)
    update_attendance("localhost",'root','nitpreet','bea',name)
  if args.calculate:
    name = input("Enter name: ")
    pay = calculate_pay("localhost",'root','nitpreet','bea',name)
    print("Your pay till date is",pay)
if __name__=="__main__":
  Main()




# count = capture_image()
# known_encodings,known_names= training(r"C:\Users\Nitpreet.Nitpreet\Desktop\BEA_Final\Dataset")
# name = prediction(r'C:\Users\Nitpreet.Nitpreet\Desktop\BEA_Final\venv\test_'+str(count-1)+'.png',known_encodings)
# update_attendance("localhost",'root','nitpreet','bea',name)
# print(result)