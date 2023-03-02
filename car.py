import cv2
import mediapipe as mp
import serial

# Set up Serial communication with Arduino
ser = serial.Serial('COM7', 9600)

# Initialize MediaPipe Hand detection module
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Set up video capture
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue
    
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect hand landmarks
    with mp_hands.Hands(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
        
        results = hands.process(gray)
        # Check if any hand is detected
        if results.multi_hand_landmarks:
            # Get landmarks of the first detected hand
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Get the x-coordinate of the tip of the index and middle fingers
            x1 = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
            x2 = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x
            
            # Get the number of fingers that are extended
            num_fingers = sum([1 for lm in hand_landmarks.landmark[1:] if lm.visibility > 0.5 and lm.y < hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y])
            
            # Control the motor based on the number and position of fingers
            if num_fingers == 5:
                ser.write(b'1')  # start motor
            elif x1 < x2:
                ser.write(b'2')  # stop left motor
                ser.write(b'3')  # start right motor
            elif x1 > x2:
                ser.write(b'3')  # stop right motor
                ser.write(b'2')  # start left motor
            elif num_fingers == 4:
                ser.write(b'4')  # reverse motor
            else:
                ser.write(b'0')  # stop motor
    
    # Display the image with landmarks
    mp_drawing.draw_landmarks(
        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    cv2.imshow('MediaPipe Hands', image)

    # Press 'q' to quit
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
