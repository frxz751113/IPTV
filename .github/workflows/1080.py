name: 1080源采集

on:
  schedule:
    - cron: '25 */6 * * *'        #这里更改自动运行的时间，没这两行的话只能手动运行
  workflow_dispatch:
    分支:
      - main
      
jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v2
    
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.x

      - name: Install dependencies
        run: pip install selenium requests futures eventlet
      - name: Install dependencies
        run: pip install replace
      - name: Install dependencies
        run: pip install input
     
      - name: Run iptv
        run: python ${{ github.workspace }}/iptv1080.py      #这里更改要运行的py

      - name: 提交更改
        run: |
          git config --local user.email "mlyuanlang@126.com"
          git config --local user.name "mlvjfchen"
          git add .
          git commit *.txt -m "Add generated file"
          # git commit *.m3u -m "Add generated file"
          #git pull --rebase
          git push -f
