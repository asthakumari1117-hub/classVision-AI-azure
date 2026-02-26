import cv2
import time
import requests

# 🔹 Azure Prediction URL (replace later)
PREDICTION_URL = "https://aictevision-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/b50c13dc-3ea3-4cf3-ad2d-d4511ab52293/classify/iterations/classroom-attention-model/image"

PREDICTION_KEY = "B7sEyTgbUWzj6VHSFTg1twgHBn3DLHlo5kntOLH5w3XOz5DWJgr2JQQJ99CBACYeBjFXJ3w3AAAIACOGIeDe"
# 🔹 Headers for Azure request
headers = {
    "Prediction-Key": PREDICTION_KEY,
    "Content-Type": "application/octet-stream"
}

# 🔹 Open webcam
camera = cv2.VideoCapture(0)

while True:
    ret, frame = camera.read()
    if not ret:
        break

    # Save image
    image_name = "captured.jpg"
    cv2.imwrite(image_name, frame)

    # Send image to Azure
    with open(image_name, "rb") as image:
        response = requests.post(PREDICTION_URL, headers=headers, data=image)

    result_text = "Detecting..."

    if response.status_code == 200:
        predictions = response.json()["predictions"]
        best = max(predictions, key=lambda x: x["probability"])
        label = best["tagName"]
        prob = round(best["probability"] * 100, 2)
        result_text = f"{label} ({prob}%)"

    # 🔹 Put text on webcam frame
    cv2.putText(
        frame,
        f"Attention: {result_text}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # Show webcam
    cv2.imshow("Classroom Attention Detection", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(5)

camera.release()
cv2.destroyAllWindows()