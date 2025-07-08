import torch
import os
from anomaly_detection import AnomalyDetector  # 반드시 클래스 정의 필요

# 변환할 .pth 파일 목록 (필요시 추가/수정)
pth_files = [
    # "actual_anomaly_detector.pth",
    # "lstm_dynamic_best_epoch92_f10.9705.pth",
    "노말변경3개.pth",
    "데증레이어3개.pth",
    "레이어3개.pth",
    # "스트그쓰느스트1.pth",
    # "스트그쓰느.pth",
    # "전이학습세팅이전.pth",
    # "추가학습패딩없이(최고).pth",
    # "추가학습패딩있이.pth",
    # "패딩없이.pth",
    # "패딩있이.pth",
    # "퓨어모델(AI허브만).pth"
]

input_shape = (1, 15, 68)  # (batch, seq_len, 17*4)

save_dir = "saved_models/pth"
os.makedirs(save_dir, exist_ok=True)

for pth_file in pth_files:
    pth_path = os.path.join(save_dir, pth_file)
    if not os.path.exists(pth_path):
        print(f"❌ 파일 없음: {pth_path}")
        continue

    # 모델 생성 및 가중치 로드
    model = AnomalyDetector()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.load_state_dict(torch.load(pth_path, map_location=device))
    model = model.to(device)
    model.eval()

    # TorchScript 변환 (입력도 같은 device)
    example_input = torch.randn(*input_shape, device=device)
    try:
        traced = torch.jit.trace(model, example_input)
        pt_name = os.path.splitext(pth_file)[0] + "_torchscript.pt"
        pt_path = os.path.join(save_dir, pt_name)
        traced.save(pt_path)
        print(f"✅ 변환 완료: {pt_path}")
    except Exception as e:
        print(f"⚠️ 변환 실패: {pth_file} ({e})")