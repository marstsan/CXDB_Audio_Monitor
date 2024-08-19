from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import pickle


class VideoVerification:
    def __init__(self, lgr):
        self.lgr = lgr
        # 1. Load the trained model
        self.model = load_model('tensorflow/video_predict.h5')
        with open("tensorflow/label_encoder.pkl", "rb") as f:
            self.encoder = pickle.load(f)

    def predict_image(self, image_path):

        # # 1. Load the trained model
        # model = load_model('tensorflow/video_predict.h5')

        # 2. Load and preprocess the image
        img = Image.open(image_path).convert('RGB')
        img = img.resize((128, 128))  # Assuming you resized images to 128x128 during training
        input_data = np.array(img).astype('float32') / 255.0  # Normalize to [0, 1]
        input_data = np.expand_dims(input_data, axis=0)  # Add batch dimension

        # 3. Make predictions
        predictions = self.model.predict(input_data)
        predicted_class = np.argmax(predictions, axis=1)

        # 4. Convert the numeric label back to the original string label
        # with open("tensorflow/label_encoder.pkl", "rb") as f:
        #     encoder = pickle.load(f)
        predicted_label = self.encoder.inverse_transform(predicted_class)[0]

        return predicted_label

    def get_predict_result(self, image, answer):
        self.lgr.info(f'[Video Verification Result] Video Verification...')
        predicted_label = self.predict_image(image)

        if answer in predicted_label:
            self.lgr.info(f'[Video Verification Result] {image} matched.')
            return True
        else:
            import shutil
            from datetime import datetime, timedelta
            self.lgr.info(f'[Video Verification Result] {image} no match found.')
            _name = image.split('/')[2]
            new_name = _name.split('.')[0]
            time_stamp = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%dT%H-%M-%SZ')
            shutil.copy(f'{image}', f'video_screenshot/error/{new_name}_{time_stamp}.png')
            return False
