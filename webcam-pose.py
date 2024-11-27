import cv2
import mediapipe as mp
import numpy as np

# Função para calcular a distância entre dois landmarks
def calculate_distance(p1, p2):
    return np.linalg.norm(np.array([p1.x, p1.y, p1.z]) - np.array([p2.x, p2.y, p2.z]))

# Função para calcular medidas corporais
def calculate_body_measurements(landmarks):
    measurements = {
        'Altura': calculate_distance(landmarks[0], landmarks[32]),
        'Braço esquerdo': calculate_distance(landmarks[11], landmarks[15]),
        'Braço direito': calculate_distance(landmarks[12], landmarks[16]),
        'Perna esquerda': calculate_distance(landmarks[23], landmarks[27]),
        'Perna direita': calculate_distance(landmarks[24], landmarks[28]),
        'Largura dos ombros': calculate_distance(landmarks[11], landmarks[12]),
        'Tronco': calculate_distance(landmarks[11], landmarks[24])
    }
    return measurements

# Função para verificar se a mão está fechada
def is_hand_closed(hand_landmarks):
    # Pontos chave: ponta dos dedos (4, 8, 12, 16, 20) e base do dedo 0 (pulso)
    # Se todas as pontas dos dedos estão próximas do pulso, consideramos a mão fechada
    closed = calculate_distance(hand_landmarks[0], hand_landmarks[9]) < 0.2 
         
    return closed

# Inicializa o Mediapipe Pose e Hands
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
pose = mp_pose.Pose()
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Acessa a webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Processa o frame
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results_pose = pose.process(rgb_frame)
    results_hands = hands.process(rgb_frame)
    
    if results_pose.pose_landmarks:
        # Desenha landmarks no frame
        mp_drawing.draw_landmarks(frame, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # Calcula medidas corporais
        landmarks = results_pose.pose_landmarks.landmark
        measurements = calculate_body_measurements(landmarks)
        
        # Exibe as medidas na tela
        y_offset = 30
        for name, value in measurements.items():
            cv2.putText(frame, f"{name}: {value:.2f}", (10, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            y_offset += 30
        
        # Verifica se há landmarks de mão e detecta o gesto de mão fechada
        if results_hands.multi_hand_landmarks:
            for hand_landmarks in results_hands.multi_hand_landmarks:
                if is_hand_closed(hand_landmarks.landmark):
                    # Salva as medidas em um arquivo
                    with open("medidas_capturadas.txt", "a") as file:
                        file.write("Medidas capturadas:\n")
                        for name, value in measurements.items():
                            file.write(f"{name}: {value:.2f}\n")
                        file.write("\n")
                    print("Medidas salvas no arquivo 'medidas_capturadas.txt'")
                    # Desenha os landmarks da mão
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    # Mostra o frame com informações
    cv2.imshow('Real-time Body Measurements', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()