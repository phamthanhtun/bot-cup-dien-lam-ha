name: Quet_Lich_Lam_Ha

on:
  schedule:
    - cron: '0 0 * * *' # Chạy lúc 7h sáng VN hàng ngày
  workflow_dispatch: # Nút bấm chạy bằng tay

jobs:
  run_bot:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pandas playwright beautifulsoup4 requests
          # Bước quan trọng nhất: Cài trình duyệt và các thư viện hệ thống đi kèm
          playwright install chromium --with-deps

      - name: Run script
        run: python main.py
        env:
          PYTHONUNBUFFERED: 1
