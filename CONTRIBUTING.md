# Contributing to ai-makeup-hairstyle-tryon-studio

Thanks for wanting to improve the studio. This is a hobbyist desktop tool
for local AI makeup and hairstyle try-on — no cloud, no accounts, no
telemetry. Keep it that way.

## Dev setup

```powershell
git clone https://github.com/tryon-studio/ai-makeup-hairstyle-tryon-studio
cd ai-makeup-hairstyle-tryon-studio
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Model weights are downloaded on first run into `%APPDATA%\tryon-studio\models`.
If you're working on the GAN stage, drop your own `makeup_gan_v2.pt` there and
update the hash in `studio/services/model_registry.py`.

## Running

```powershell
tryon-studio
```

## Tests

```powershell
p