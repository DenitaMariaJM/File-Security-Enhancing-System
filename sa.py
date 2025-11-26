import tkinter as tk
import cv2
import threading
from PIL import Image, ImageTk
import numpy as np
import os
from match_checker import get_locs,check
from tkinter import filedialog, messagebox
from cryp import enc, dec


class WebcamApp:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.vid = cv2.VideoCapture(self.video_source)

        self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.canvas = tk.Canvas(window, width=self.width, height=self.height)
        self.canvas.pack()

        self.btn_encrypt = tk.Button(window, text="Encrypt File", width=25, height=2, command=self.encrypt_file)
        self.btn_encrypt.pack(pady=5)

        self.btn_decrypt = tk.Button(window, text="Decrypt File", width=25, height=2,command=self.decrypt_file)
        self.btn_decrypt.pack(pady=5)

        self.btn_exit = tk.Button(window, text="Exit", width=25, height=2, command=self.quit_app)
        self.btn_exit.pack(pady=5)

        # Load the DNN face detection model
        self.net = cv2.dnn.readNetFromCaffe(
        "C:/Users/user/Downloads/miniproject/models/deploy.prototxt",
            "C:/Users/user/Downloads/miniproject/models/res10_300x300_ssd_iter_140000.caffemodel"
        )


        self.frame_count = 0  # For optimizing frame processing
        self.update_video()

    def detect_faces_dnn(self, frame):
        """Detect faces using OpenCV DNN model."""
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, scalefactor=1.0, size=(300, 300), mean=(104.0, 177.0, 123.0))
        self.net.setInput(blob)
        detections = self.net.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.6:  # Confidence threshold
                box = detections[0, 0, i, 3:7] * [w, h, w, h]
                (x, y, x2, y2) = box.astype("int")
                faces.append((x, y, x2 - x, y2 - y))

        return faces

    def update_video(self):
        ret, frame = self.vid.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # DNN Face Detection
            blob = cv2.dnn.blobFromImage(rgb_frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
            self.net.setInput(blob)
            detections = self.net.forward()

                # Draw face detection boxes
            for i in range(detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    if confidence > 0.5:  # Minimum confidence threshold
                        box = detections[0, 0, i, 3:7] * np.array([self.width, self.height, self.width, self.height])
                        (x, y, x1, y1) = box.astype("int")
                        cv2.rectangle(rgb_frame, (x, y), (x1, y1), (0, 255, 0), 2)

        # Convert frame to ImageTk format and update canvas
            pil_img = Image.fromarray(rgb_frame)
            self.img = ImageTk.PhotoImage(image=pil_img)

        # Instead of creating a new image, update existing canvas image
            if hasattr(self, "canvas_image"):
                self.canvas.itemconfig(self.canvas_image, image=self.img)
            else:
                self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)

        self.window.after(10, self.update_video) 
    def choose_file(self):
        file_path = filedialog.askopenfilename(title="Choose a file to encrypt")
        print(file_path)
        return file_path 
    def encrypt_file(self):
        img = self.capture_image()
        if img:
            file = self.choose_file() 
            images = os.listdir(".\\captured_images")
            hit = 0
            a = 0
            for image in images:
                if image!=img:
                    a = check(".\\captured_images\\"+image,".\\captured_images\\"+img)
                    if a:
                        hit = 1
                        msg = enc(file,get_locs(".\\captured_images\\"+image))
                        if msg:
                            messagebox.showinfo("file successfully encrytped","file succesfully secured!!")
                            os.remove(file)
                        else:
                            messagebox.showerror("encryption failed","error in encryption")
                        os.remove("./captured_images/"+img)
                        break
            if not hit:
                msg = enc(file,get_locs(".\\captured_images\\"+img))
                if msg:
                    messagebox.showinfo("file successfully encrytped","file is secured")
                else:
                    messagebox.showerror("encryption failed","error in encryption")

    def decrypt_file(self):
        img = self.capture_image()
        if img:
            file = self.choose_file() 
            images = os.listdir(".\\captured_images")
            print(images)
            hit = 0
            a = 0
            for image in images:
                if image!=img:
                    a = check(".\\captured_images\\"+image,".\\captured_images\\"+img)
                    if a:
                        hit = 1
                        os.remove("./captured_images/"+img)
                        msg = dec(file,get_locs(".\\captured_images\\"+image))
                        if msg:
                            messagebox.showinfo("file successfully decrypted","you can access it now")
                            os.remove(file)
                        else:
                            messagebox.showerror("decryption failed","error in decryption!! unauthorized acces")
                        break
            if not a:
                messagebox.showerror("decryption failed","unauthorized access")
            if not hit: os.remove("./captured_images/"+img)
    def process_frame(self, frame):
        """Process each frame and update the Tkinter UI."""
        self.frame_count = (self.frame_count + 1) % 3  # Process every 3rd frame
        if self.frame_count != 0:
            self.window.after(10, self.update_video)
            return

        frame = cv2.resize(frame, (320, 240))  # Resize to improve performance
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.detect_faces_dnn(frame)

        for (x, y, w, h) in faces:
            cv2.rectangle(rgb_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        pil_img = Image.fromarray(rgb_frame)
        self.img = ImageTk.PhotoImage(image=pil_img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)

        self.window.after(10, self.update_video)

    def quit_app(self):
        """Close the application."""
        self.vid.release()
        self.window.destroy()
    
    def capture_image(self):
     ret, frame = self.vid.read()
     if ret:
        faces = self.detect_faces_dnn(frame)  # Use DNN instead of face_cascade
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if not os.path.exists('captured_images'):
                os.makedirs('captured_images')

            image_name = f"{len(os.listdir('captured_images')) + 1}.jpg"
            image_path = os.path.join('captured_images', image_name)
            cv2.imwrite(image_path, frame)
            return image_name
        else:
            messagebox.showwarning("No Face Detected", "No face detected. Try again.")

    # Run the application
window = tk.Tk()
app = WebcamApp(window, "DNN Face Detection with Tkinter")
window.mainloop()
