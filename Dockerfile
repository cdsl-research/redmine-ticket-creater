FROM python:3.8
# 作業ディレクトリ
WORKDIR /app
# 現在のディレクトリの内容をコンテナ内の/appにコピー
COPY . /app
# パッケージのインストール
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["flask", "run", "--host=0.0.0.0"]

# コンテナ起動時にapp.pyを実行
CMD ["python", "app.py"]
