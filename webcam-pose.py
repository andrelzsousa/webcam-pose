import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from utils import load_last_measurements, execute_notebook

# Função para calcular a distância entre dois landmarks
def calculate_distance(p1, p2):
    return np.linalg.norm(np.array([p1.x, p1.y, p1.z]) - np.array([p2.x, p2.y, p2.z]))

# Função para calcular medidas corporais
def calculate_body_measurements(landmarks):
    measurements = {
        'Altura': calculate_distance(landmarks[0], landmarks[32]) + 1.05,
        'Braco esquerdo': calculate_distance(landmarks[11], landmarks[15]) + 0.52,
        'Braco direito': calculate_distance(landmarks[12], landmarks[16]) + 0.52,
        'Perna esquerda': calculate_distance(landmarks[23], landmarks[27]) + 0.56,
        'Perna direita': calculate_distance(landmarks[24], landmarks[28]) + 0.56,
        'Largura dos ombros': calculate_distance(landmarks[11], landmarks[12]) + 0.34,
        'Tronco': calculate_distance(landmarks[11], landmarks[24])+ 0.4
    }
    return measurements

def is_hand_closed(hand_landmarks):
    closed = calculate_distance(hand_landmarks[0], hand_landmarks[9]) < 0.2 
         
    return closed

# Função principal para capturar vídeo e exibir medidas
def start_video(peso, idade):
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
            
            # Exibe as medidas e informações na tela
            y_offset = 35
            cv2.putText(frame, f"Peso: {peso:.1f} kg", (10, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            y_offset += 35
            cv2.putText(frame, f"Idade: {idade} anos", (10, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            y_offset += 35
            for name, value in measurements.items():
                cv2.putText(frame, f"{name}: {value:.2f}", (10, y_offset), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
                y_offset += 35
            
            # Verifica se há landmarks de mão e detecta o gesto de mão fechada
            if results_hands.multi_hand_landmarks:
                for hand_landmarks in results_hands.multi_hand_landmarks:
                    if is_hand_closed(hand_landmarks.landmark):
                        # Salva as medidas em um arquivo
                        with open("medidas_capturadas_ui.txt", "a") as file:
                            file.write("Medidas capturadas:\n")
                            file.write(f"Peso: {peso:.1f} kg\n")
                            file.write(f"Idade: {idade} anos\n")
                            print(f"peso: {peso}, idade: {idade} ")
                            for name, value in measurements.items():
                                file.write(f"{name}: {value:.2f}\n")
                                print(f"{name}: {value:.2f}\n")
                            file.write("\n")
                            print("\n\n\n\n\n\n\n\n")
                        print("Medidas salvas no arquivo 'medidas_capturadas_ui.txt'")
                        # Desenha os landmarks da mão
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # Mostra o frame com informações
        cv2.imshow('Real-time Body Measurements', frame)

        if cv2.waitKey(1) & 0xFF == ord('p'):
          data = load_last_measurements("medidas_capturadas_ui.txt")
          if data:
              print(f"Dados carregados: Peso={data[0]}, Idade={data[1]}, Altura={data[2]}")
              peso, idade, altura = data
              print(f"Dados carregados: Peso={peso}, Idade={idade}, Altura={altura}")
              execute_notebook(
                  input_path="clothes.ipynb",
                  output_path="output_clothes.ipynb",
                  parameters={"peso": peso, "idade": idade, "altura": altura}
        )
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal
    
    # Coleta peso e idade do usuário
    peso = simpledialog.askfloat("Informação", "Digite seu peso (em kg):")
    idade = simpledialog.askinteger("Informação", "Digite sua idade:")
    
    if peso is not None and idade is not None:
        messagebox.showinfo("Instruções", "Aperte 'Q' para sair. Feche a mão para salvar as medidas.")
        start_video(peso, idade)
    else:
        messagebox.showerror("Erro", "Peso ou idade não foram fornecidos. Saindo do programa.")

if __name__ == "__main__":
    main()