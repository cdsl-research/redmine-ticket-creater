# redmine-ticket-creater
このシステムはAlertmanagerから通知されたアラートをチケットにするものです．Pythonによって実装されています．

### 環境
- Ubuntu 24.04.1 LTS
- Python 3.10.12
- K3s
- Prometheus
- Alertmanager
- Redmine

### Pythonライブラリ
- flask
- requests
- json
- datetime
- os

### 流れ

流れは以下になります．Prometheusがexporterから取得したメトリクスをもとにアラートを発行します．Alertmanagerはそのアラートを通知する役割があります．今回は通知先としてredmine-ticket-createrを選択します．




<img width="416" alt="image" src="https://github.com/user-attachments/assets/c850c213-510a-40f3-8a3b-f702440a5ec2" />


Alertmanagerでの通知先の設定は以下の記事を参考にしてください．
- https://github.com/cdsl-research/Prometheus-tmp-cdsl
- https://qiita.com/g21240349d/items/7886980954ad218e90be




### 構成要素

```
redmine-ticket-creater
├── deploy/
│   ├── ticket-create-deployment.yaml #Kubernetesで動かす時のdeployment用ファイル
│   └──  ticket-create-service.yaml #Kubernetesで動かす時のservice用ファイル
│  
├── Dockerfile 
│   
├── app.py #redmine-ticket-createrの実行ファイル
├── requirements.txt #ライブラリのインストール用ファイル
└── schedule.json# スケジュールせってようファイル
```


### 使い方

1. 対象のディレクトリに移動
```
monitoring@monitoring-dev-master:~$ cd redmine-ticket-creater
monitoring@monitoring-dev-master:~/redmine-ticket-creater$ pwd
/home/monitoring/redmine-ticket-creater
monitoring@monitoring-dev-master:~/redmine-ticket-creater$ 
```

2. 仮想環境の作成
```
monitoring@monitoring-dev-master:~/redmine-ticket-creater$ python3 -m venv redmine
monitoring@monitoring-dev-master:~/redmine-ticket-creater$ source redmine/bin/activate
(redmine) monitoring@monitoring-dev-master:~/redmine-ticket-creater$ 
```

3. 必要なライブラリのインストール
```
(redmine) monitoring@monitoring-dev-master:~/redmine-ticket-creater$ pip install -r requirements.txt
Collecting Flask==2.3.3 (from -r requirements.txt (line 1))
  Downloading flask-2.3.3-py3-none-any.whl.metadata (3.6 kB)
Collecting requests==2.31.0 (from -r requirements.txt (line 2))
  Downloading requests-2.31.0-py3-none-any.whl.metadata (4.6 kB)
Collecting Werkzeug>=2.3.7 (from Flask==2.3.3->-r requirements.txt (line 1))
  Downloading werkzeug-3.1.3-py3-none-any.whl.metadata (3.7 kB)
Collecting Jinja2>=3.1.2 (from Flask==2.3.3->-r requirements.txt (line 1))
  Downloading jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Collecting itsdangerous>=2.1.2 (from Flask==2.3.3->-r requirements.txt (line 1))
  Downloading itsdangerous-2.2.0-py3-none-any.whl.metadata (1.9 kB)
Collecting click>=8.1.3 (from Flask==2.3.3->-r requirements.txt (line 1))
  Downloading click-8.2.1-py3-none-any.whl.metadata (2.5 kB)
Collecting blinker>=1.6.2 (from Flask==2.3.3->-r requirements.txt (line 1))
  Downloading blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
Collecting charset-normalizer<4,>=2 (from requests==2.31.0->-r requirements.txt (line 2))
  Downloading charset_normalizer-3.4.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (35 kB)
Collecting idna<4,>=2.5 (from requests==2.31.0->-r requirements.txt (line 2))
  Downloading idna-3.10-py3-none-any.whl.metadata (10 kB)
Collecting urllib3<3,>=1.21.1 (from requests==2.31.0->-r requirements.txt (line 2))
  Downloading urllib3-2.5.0-py3-none-any.whl.metadata (6.5 kB)
Collecting certifi>=2017.4.17 (from requests==2.31.0->-r requirements.txt (line 2))
  Downloading certifi-2025.6.15-py3-none-any.whl.metadata (2.4 kB)
Collecting MarkupSafe>=2.0 (from Jinja2>=3.1.2->Flask==2.3.3->-r requirements.txt (line 1))
  Downloading MarkupSafe-3.0.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.0 kB)
Downloading flask-2.3.3-py3-none-any.whl (96 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 96.1/96.1 kB 12.4 MB/s eta 0:00:00
Downloading requests-2.31.0-py3-none-any.whl (62 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 62.6/62.6 kB 15.8 MB/s eta 0:00:00
Downloading blinker-1.9.0-py3-none-any.whl (8.5 kB)
Downloading certifi-2025.6.15-py3-none-any.whl (157 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 157.7/157.7 kB 31.7 MB/s eta 0:00:00
Downloading charset_normalizer-3.4.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (148 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 148.6/148.6 kB 32.2 MB/s eta 0:00:00
Downloading click-8.2.1-py3-none-any.whl (102 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 102.2/102.2 kB 23.2 MB/s eta 0:00:00
Downloading idna-3.10-py3-none-any.whl (70 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 70.4/70.4 kB 16.3 MB/s eta 0:00:00
Downloading itsdangerous-2.2.0-py3-none-any.whl (16 kB)
Downloading jinja2-3.1.6-py3-none-any.whl (134 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 134.9/134.9 kB 27.8 MB/s eta 0:00:00
Downloading urllib3-2.5.0-py3-none-any.whl (129 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 129.8/129.8 kB 24.7 MB/s eta 0:00:00
Downloading werkzeug-3.1.3-py3-none-any.whl (224 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 224.5/224.5 kB 42.7 MB/s eta 0:00:00
Downloading MarkupSafe-3.0.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (23 kB)
Installing collected packages: urllib3, MarkupSafe, itsdangerous, idna, click, charset-normalizer, certifi, blinker, Werkzeug, requests, Jinja2, Flask
Successfully installed Flask-2.3.3 Jinja2-3.1.6 MarkupSafe-3.0.2 Werkzeug-3.1.3 blinker-1.9.0 certifi-2025.6.15 charset-normalizer-3.4.2 click-8.2.1 idna-3.10 itsdangerous-2.2.0 requests-2.31.0 urllib3-2.5.0
(redmine) monitoring@monitoring-dev-master:~/redmine-ticket-creater$ 
```

4. schedule.jsonの編集
それぞれの曜日の箇所と***の部分に時間とredmineで登録されているユーザIDを入れる．

確認の仕方は以下の通りである．
```
$ curl http://[redmine server]/users.json?key=[APIキー]
```

```
{
  "Monday": {
    "00:00-01:30": "***",
    "01:30-03:00": "***",
    "03:00-05:30": "***",
    "05:30-09:00": "***"
  },
  "Tuesday": {
    "00:00-01:30": "***",
    "01:30-03:00": "***",
    "03:00-05:30": "***",
    "05:30-09:00": "***"
  },
  "Wednesday": {
    "00:00-01:30": "***",
    "01:30-03:00": "***",
    "03:00-05:30": "***",
    "05:30-09:00": "***"
  },
  "Thursday": {
    "00:00-01:30": "***",
    "01:30-03:00": "***",
    "03:00-05:30": "***",
    "05:30-09:00": "***"
  },
  "Friday": {
    "00:00-01:30": "***",
    "01:30-03:00": "***",
    "03:00-05:30": "***",
    "05:30-09:00": "***"
  }
}

```


5. app.py内以下の箇所にRedmineのAPIのURL，APIのkey，ProjectのID，TrackのIDを入力する．
```
REDMINE_URL = os.environ['REDMINE_URL']
API_KEY = os.environ['API_KEY']
PROJECT_ID = os.environ['PROJECT_ID']
Track_ID = os.environ['Track_ID']
```

環境変数で設定する場合は以下のようにする
```
export REDMINE_URL="https://your-redmine.example.com"
export API_KEY="your_redmine_api_key"
export PROJECT_ID="your_project_id"
export Track_ID="your_track_id"
```


6. 実行
以下のようにflaskが起動すればOK
```
monitoring@monitoring-master-ml:~/redmine-ticket-create$ source redmine/bin/activate
(redmine) monitoring@monitoring-master-ml:~/redmine-ticket-create$ python3 app.py 
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
 * Running on http://192.168.100.76:8000
Press CTRL+C to quit
```

7. 確認
ブラウザでredmineにチケットがあるのかを確認しましょう．
http://<redmineの配置されている対象のIP or Host名>:<公開したPort>で見れます．

<img width="851" alt="スクリーンショット 2025-07-06 14 07 16" src="https://github.com/user-attachments/assets/f01571bc-c45b-47cc-a1d1-1e6ae8fb762d" />

このようにAlertの通知からチケットが作成されていればOKです．





