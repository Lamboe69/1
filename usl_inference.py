import torch
import torch.nn as nn
import cv2
import numpy as np

class RealUSLModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.video_encoder = nn.Sequential(
            nn.Conv3d(3, 32, (3, 7, 7), padding=(1, 3, 3)), nn.ReLU(), nn.MaxPool3d((1, 2, 2)),
            nn.Conv3d(32, 64, (3, 5, 5), padding=(1, 2, 2)), nn.ReLU(), nn.MaxPool3d((2, 2, 2)),
            nn.Conv3d(64, 128, (3, 3, 3), padding=1), nn.ReLU(), nn.AdaptiveAvgPool3d((1, 1, 1))
        )
        self.classifier = nn.Sequential(nn.Dropout(0.5), nn.Linear(128, 64), nn.ReLU(), nn.Dropout(0.3), nn.Linear(64, 8))
        
    def forward(self, x):
        x = x.permute(0, 2, 1, 3, 4)
        features = self.video_encoder(x).view(x.size(0), -1)
        return self.classifier(features)

def load_usl_model():
    checkpoint = torch.load('complete_usl_model.pth', map_location='cpu')
    model = RealUSLModel()
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    return model, checkpoint

def predict_usl_video(model, video_path):
    disease_classes = ['malaria', 'tuberculosis', 'typhoid', 'cholera', 'measles', 'viral_hemorrhagic_fever', 'covid_like', 'general']
    
    cap = cv2.VideoCapture(video_path)
    frames = []
    for _ in range(16):
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.resize(frame, (64, 64))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame)
    cap.release()
    
    while len(frames) < 16:
        frames.append(frames[-1] if frames else np.zeros((64, 64, 3)))
    
    video = torch.FloatTensor(frames).permute(0, 3, 1, 2).unsqueeze(0) / 255.0
    
    with torch.no_grad():
        outputs = model(video)
        probabilities = torch.softmax(outputs, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0, predicted_class].item()
    
    return {'predicted_disease': disease_classes[predicted_class], 'confidence': confidence}

if __name__ == "__main__":
    model, info = load_usl_model()
    print(f"USL Model loaded: {info['accuracy']}% accuracy")