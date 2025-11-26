import face_recognition
import hashlib
from deepface import DeepFace

def check(image1_path, image2_path):
    try:
        result = DeepFace.verify(image1_path, image2_path)
        if result["verified"]:
            return 1
        return 0
    except Exception as e:
        print("An error occurred:", str(e))

def encode_string_sha256(input_string):
    encoded_string = input_string.encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(encoded_string)
    hashed_string = sha256_hash.hexdigest()
    return hashed_string

def load_image(image_path):
    # Load image and return the face encoding
    image = face_recognition.load_image_file(image_path)
    face_encoding = face_recognition.face_encodings(image)
    l = ""
    for i in face_encoding[0]:
        l+=str(i)
    print("\n\n\n\n")
    print(encode_string_sha256(l))
    if len(face_encoding) > 0:
        return face_encoding[0]
    else:
        return None

def get_locs(image_path):
    image = face_recognition.load_image_file(image_path)
    face_encoding = face_recognition.face_encodings(image)
    l = ""
    for i in face_encoding[0]:
        l+=str(i)
    return encode_string_sha256(l)

def compare_faces(face_encoding1, face_encoding2):
    # Compare the face encodings and return True if they match, False otherwise
    if face_encoding1 is not None and face_encoding2 is not None:
        results = face_recognition.compare_faces([face_encoding1], face_encoding2)
        return results[0]
    else:
        return False


