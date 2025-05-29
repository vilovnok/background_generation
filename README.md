# ManIS
Проект ManIS был реализован на [hack](https://aiproducthack.com/).
Основная задача этого проекта - создание фона для заданного изображения мебели.

## Входное изображение → Модель → Выходное изображение

| Вход (Input) | Модель | Выход (Output) |
|--------------|--------|----------------|
| ![input](images/sofa.webp) | 🤖 | ![output](images/output.png) |


### Pipeline Build:

#### Install requirements:
```bash
conda create -n "basa" python=3.10
conda activate basa
pip install -r base_requirements.txt
pip install git+https://github.com/sberbank-ai/Real-ESRGAN.git
```

#### Load model weights:
```bash
gdown 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
unzip weights.zip -d weights
```

