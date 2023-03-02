import cv2
import mediapipe as mp
from serial import Serial


# Initialize the serial connection to the Arduino
ser = Serial('COM7', 9600)  # Replace 'COM3' with the appropriate port number

# Initialize the mediapipe hand detection module
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialize the video capture object
cap = cv2.VideoCapture(0)

# Define the thresholds for finger detection
THUMB_THRESHOLD = 0.9
FOUR_FINGER_THRESHOLD = 0.7
TWO_FINGER_THRESHOLD = 0.3

while True:
    # Read a frame from the video stream
    ret, frame = cap.read()
    
    # Flip the frame horizontally to make it easier to work with
    frame = cv2.flip(frame, 1)
    
    # Convert the frame to RGB for processing with mediapipe
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Run the mediapipe hand detection on the frame
    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        results = hands.process(image)
        
        # Draw the hand landmarks on the frame
        annotated_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                # Extract the finger landmark points
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                
                # Determine if the hand is open or closed based on the thumb position
                if thumb_tip.y < index_tip.y < middle_tip.y < ring_tip.y < pinky_tip.y:
                    # Hand is open, start both motors
                    ser.write(b'11')
                else:
                    # Hand is closed, stop both motors
                    ser.write(b'00')
                
                # Determine which fingers are extended
                thumb_extended = thumb_tip.y < index_tip.y
                four_fingers_extended = index_tip.y < middle_tip.y < ring_tip.y < pinky_tip.y
                two_fingers_extended = index_tip.y < middle_tip.y and ring_tip.y < pinky_tip.y
                
                # Control the motors based on the finger positions
                if four_fingers_extended and thumb_extended:
                    # All five fingers are extended, start both motors
                    ser.write(b'11')
                elif two_fingers_extended:
                    # Only two fingers are extended, start the right motor
                    ser.write(b'10')
                elif not thumb_extended and four_fingers_extended:
                    ser.write(b,'01')
                    # Only three fingers are
