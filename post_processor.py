import matplotlib.pyplot as plt
from PIL import Image
from RealESRGAN import RealESRGAN
from tqdm import tqdm


class PostProcessor:
    def __init__(self, device):
        self.upscaler = RealESRGAN(device, scale=4)
        self.upscaler.load_weights("weights/RealESRGAN_x4.pth", download=True)

    def __call__(self, images: list[Image]) -> list[Image]:
        result_images = []
        for idx, img in enumerate(tqdm(images, desc="Upscaling images")):
            sr_image = self.upscaler.predict(img)
            result_images.append(sr_image)
        return result_images        
    @staticmethod
    def make_plot(img_list, fig_path):
        fig = plt.figure(figsize=(20, 20))
        assert len(img_list) % 10 == 0
        column_num = 5
        raws_num = len(img_list) // column_num
        for i, img in enumerate(img_list):
            img = img.resize((512, 512))
            ax = fig.add_subplot(4, 5, i + 1)
            ax.set_title(f"img_number_{i + 1}")
            ax.imshow(img)
            ax.axis("off")

        plt.subplots_adjust(wspace=0.1, hspace=0.5)
        plt.savefig(fig_path)
        plt.show()
