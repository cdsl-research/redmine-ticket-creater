# redmine-ticket-creater
このシステムはAlertmanagerから通知されたアラートをチケットにするものです．Pythonによって実装されています．

### 環境
- Ubuntu 24.04.1 LTS
- Python 3.10.12
- K3s 1.30.6+k3s1
- Prometheus 2.53.1
- Alertmanager 0.27.0
- Redmine 6.0.4.stable

### Pythonライブラリ
- flask 2.3.3
- requests 2.31.0
- json
- datetime
- os

### 流れ

流れは以下になります．Prometheusがexporterから取得したメトリクスをもとにアラートを発行します．Alertmanagerはそのアラートを通知する役割があります．今回は通知先としてredmine-ticket-createrを選択します．




<img width="416" alt="image" src="https://github.com/user-attachments/assets/c850c213-510a-40f3-8a3b-f702440a5ec2" />


Alertmanagerでの通知先の設定は以下の記事を参考にしてください．
この記事にはAlertManagerの設定ファイルの内容とどのようにアラートを通知すればいいのかを書いてあります！
- AlertManagerの通知をjobごとに分ける(実例を交えながらやってみた) URL → https://qiita.com/g21240349d/items/7886980954ad218e90be




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
それぞれの曜日の箇所と***の部分に時間とredmineで登録されているユーザIDを入れる．時間はUTC時間で入れてください．

確認の仕方は以下の通りである．
```
$ curl http://[redmine server]/users.json?key=[APIキー]
```

実際にやってみると以下のような出力が出ます．
```
monitoring@monitoring-master-ml:~/redmine-ticket-create$ curl http://localhost:32300/users.json?key=d5ec3e180eb1b8344641be07cf1a6850eeb87ecb
{"users":[{"id":13,"login":"akram","admin":false,"firstname":"アクラム","lastname":"ムハマド","mail":"akram@test","created_on":"2025-04-21T05:22:41Z","updated_on":"2025-05-19T00:10:33Z","last_login_on":"2025-06-17T02:23:26Z","passwd_changed_on":"2025-04-21T05:22:41Z","twofa_scheme":null,"status":1},{"id":19,"login":"arita","admin":false,"firstname":"海斗","lastname":"有田","mail":"c0a22006b2@edu.teu.ac.jp","created_on":"2025-04-23T00:47:55Z","updated_on":"2025-04-23T04:39:28Z","last_login_on":"2025-07-08T03:50:43Z","passwd_changed_on":"2025-04-23T04:39:28Z","twofa_scheme":null,"status":1},{"id":9,"login":"hirao","admin":true,"firstname":"真斗","lastname":"平尾","mail":"hirao@test","created_on":"2025-04-17T06:52:33Z","updated_on":"2025-04-23T00:37:43Z","last_login_on":"2025-07-14T12:52:06Z","passwd_changed_on":"2025-04-17T06:52:33Z","twofa_scheme":null,"status":1},{"id":15,"login":"ide","admin":false,"firstname":"佑","lastname":"井出","mail":"ide@test","created_on":"2025-04-22T05:46:35Z","updated_on":"2025-04-22T05:46:35Z","last_login_on":"2025-07-10T06:11:10Z","passwd_changed_on":"2025-04-22T05:46:35Z","twofa_scheme":null,"status":1},{"id":17,"login":"kitagawa","admin":false,"firstname":"翔也","lastname":"北川","mail":"kitagawa@test","created_on":"2025-04-22T05:47:58Z","updated_on":"2025-04-22T05:47:58Z","last_login_on":"2025-07-14T23:20:08Z","passwd_changed_on":"2025-04-22T05:47:58Z","twofa_scheme":null,"status":1},{"id":10,"login":"koyama","admin":true,"firstname":"智之","lastname":"小山","mail":"d212400159@edu.teu.ac.jp","created_on":"2025-04-21T04:45:50Z","updated_on":"2025-04-25T07:17:26Z","last_login_on":"2025-06-17T02:13:30Z","passwd_changed_on":"2025-04-23T00:21:19Z","twofa_scheme":null,"status":1},{"id":14,"login":"kushida","admin":false,"firstname":"高幸","lastname":"串田","mail":"kushida@test","created_on":"2025-04-21T05:31:38Z","updated_on":"2025-04-21T05:31:38Z","last_login_on":null,"passwd_changed_on":"2025-04-21T05:31:38Z","twofa_scheme":null,"status":1},{"id":8,"login":"okada","admin":false,"firstname":"京太郎","lastname":"岡田","mail":"okada@test","created_on":"2025-04-17T06:51:40Z","updated_on":"2025-04-17T07:14:17Z","last_login_on":"2025-07-10T01:38:22Z","passwd_changed_on":"2025-04-17T06:51:40Z","twofa_scheme":null,"status":1},{"id":18,"login":"osawa","admin":false,"firstname":"恭平","lastname":"大沢","mail":"osawa@test","created_on":"2025-04-22T05:50:02Z","updated_on":"2025-04-22T05:50:02Z","last_login_on":"2025-05-16T01:18:17Z","passwd_changed_on":"2025-04-22T05:50:02Z","twofa_scheme":null,"status":1},{"id":5,"login":"sakai","admin":true,"firstname":"萌桜","lastname":"坂井","mail":"sakai@test","created_on":"2025-04-17T06:46:36Z","updated_on":"2025-04-23T00:52:43Z","last_login_on":"2025-07-14T03:51:21Z","passwd_changed_on":"2025-04-17T06:46:36Z","twofa_scheme":null,"status":1},{"id":7,"login":"sato","admin":false,"firstname":"健斗","lastname":"佐藤","mail":"sato@test","created_on":"2025-04-17T06:50:26Z","updated_on":"2025-04-17T07:14:34Z","last_login_on":"2025-07-10T03:31:17Z","passwd_changed_on":"2025-04-17T06:50:26Z","twofa_scheme":null,"status":1},{"id":11,"login":"teduka","admin":false,"firstname":"雄星","lastname":"手塚","mail":"teduka@test","created_on":"2025-04-21T04:48:07Z","updated_on":"2025-04-21T04:48:07Z","last_login_on":"2025-07-10T08:45:25Z","passwd_changed_on":"2025-04-21T04:48:07Z","twofa_scheme":null,"status":1},{"id":21,"login":"ticket_create","admin":true,"firstname":"ticket","lastname":"create","mail":"ticket@create","created_on":"2025-05-08T01:41:32Z","updated_on":"2025-05-08T01:41:32Z","last_login_on":"2025-05-13T03:05:51Z","passwd_changed_on":"2025-05-08T01:41:32Z","twofa_scheme":null,"status":1},{"id":6,"login":"tukimori","admin":true,"firstname":"陽太","lastname":"月森","mail":"tukimori@test","created_on":"2025-04-17T06:49:37Z","updated_on":"2025-07-01T05:17:35Z","last_login_on":"2025-07-14T08:20:43Z","passwd_changed_on":"2025-04-17T06:49:37Z","twofa_scheme":null,"status":1},{"id":16,"login":"yamazaki","admin":false,"firstname":"雅也","lastname":"山崎","mail":"yamazaki@test","created_on":"2025-04-22T05:47:19Z","updated_on":"2025-04-22T05:47:19Z","last_login_on":"2025-06-26T03:07:47Z","passwd_changed_on":"2025-04-22T05:47:19Z","twofa_scheme":null,"status":1},{"id":22,"login":"yamazaki.t","admin":false,"firstname":"拓海","lastname":"山崎","mail":"yamazaki.t@test","created_on":"2025-05-20T01:49:32Z","updated_on":"2025-05-20T01:49:32Z","last_login_on":"2025-07-14T01:49:54Z","passwd_changed_on":"2025-05-20T01:49:32Z","twofa_scheme":null,"status":1}],"total_count":16,"offset":0,"limit":25}monitoring@monitoring-master-ml:~/redmine-ticket-create$ 
```


このidの箇所を以下の`schedule.json`に入力します．下の例は実際に私が所属する研究室で行っている設定です．
```
{
  "Monday": {
    "00:00-01:30": 22,
    "01:30-03:00": 7,
    "03:00-05:30": 6,
    "05:30-09:00": 8
  },
  "Tuesday": {
    "00:00-01:30": 6,
    "01:30-03:00": 6,
    "03:00-05:30": 22,
    "05:30-09:00": 5
  },
  "Wednesday": {
    "00:00-01:30": 5,
    "01:30-03:00": 22,
    "03:00-05:30": 6,
    "05:30-09:00": 8
  },
  "Thursday": {
    "00:00-01:30": 22,
    "01:30-03:00": 8,
    "03:00-05:30": 7,
    "05:30-09:00": 6
  },
  "Friday": {
    "00:00-01:30": "6",
    "01:30-03:00": "8",
    "03:00-05:30": "22",
    "05:30-09:00": "7"
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
このようにFlaskのAPIが待ち構えれば準備完了です．


### テスト

このプログラムが実際に動作するかどうかをテストします．このテストは上で紹介した「使い方」の章を行った後に行ってください．

1. Redmineのブラウザの画面を確認

最初にRedmineブラウザを確認してみましょう．
<img width="1026" height="680" alt="スクリーンショット 2025-07-15 12 07 52" src="https://github.com/user-attachments/assets/c14ba3ba-5cb0-458a-9cba-f5205a85f8f2" />

最初に3件だけチケットが登録されています．

2. Prometheusのルール設定

Prometheusの設定用に作成した以下のURLを参考に行いましょう．Prometheusの構築の仕方はREADMEに書いているので参考にしてください．
https://github.com/cdsl-research/Prometheus-tmp-cdsl

Prometheusの設定ファイル上にある`Prometheus-tmp-cdsl/monitoring-rule/test-alert`上にある`test-alert.yaml`に以下の設定を入れましょう．

```yaml
### テストアラート
apiVersion: v1
kind: ConfigMap
metadata:
  name: test-alert
  namespace: monitoring
data:
  nas-monitoring-rules.yml: |-
    groups:
    - name: Internal-NAS-Check
      rules:
      - alert: NAS Test Alert
        annotations:
          alert_title: "Test Alert for NAS Monitoring"
          description: "This is a test alert to verify rule configuration."
          runbook_url: https://cdsl-tut.esa.io/posts/3114
          summary: "Test alert for single instance"
        expr: vector(1)
        for: 1m
        labels:
          severity: warning
```

3. Alertmanagerの設定

Alertmanagerの設定ファイルが`Prometheus-tmp-cdsl/alert-manager`上にある`alertmanager-config.yaml`に以下の設定を入れましょう．
```yaml
・・・
 - name: 'redmine'
        webhook_configs:
          - url: 'http://monitoring-master-ml:8000/alert'
            send_resolved: false
・・・
```

これでAlertmanagerの通知対象をどこに設定するのかを決めます．

これらを適応させてテストをします．
適応させる際は`Prometheus-tmp-cdsl`上にある`restart.sh`を実行します．
```
monitoring@monitoring-master-ml:~/Prometheus-tmp-cdsl$ ./restart.sh 
deployment.apps/prometheus restarted
deployment.apps/alertmanager restarted
monitoring@monitoring-master-ml:~/Prometheus-tmp-cdsl$ 
```

そうするとPrometheusとAlertmanagerの設定が変わります．


4. チケットが登録されているかを確認

Prometheusのエンドポイントに対してブラウザからアクセスしましょう．

http://<PrometheusのエンドポイントのIP or Host名>:<Port番号>/alerts

<img width="1063" height="385" alt="スクリーンショット 2025-07-15 12 26 09" src="https://github.com/user-attachments/assets/d4495bf7-d75d-4178-9f9e-4dc61d2e1cae" />

このように追加されたアラートが登録されて，アラートがPushされています．



Flaskで作成したソフトウェアも見てみると以下のようにPostされています．
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
10.42.0.0 - - [15/Jul/2025 04:20:41] "POST /alert HTTP/1.1" 200 -
```


 確認
ブラウザでredmineにチケットがあるのかを確認しましょう．
http://<redmineの配置されている対象のIP or Host名>:<公開したPort>で見れます．

<img width="1026" height="680" alt="スクリーンショット 2025-07-15 12 07 52" src="https://github.com/user-attachments/assets/1da7d489-7001-4da0-9e90-a292bcda09bb" />


チケットが新たに追加されていますね．
このようにAlertの通知からチケットが作成されていればOKです．


### 最後に

今回はAlertmanagerのアラートからチケットを登録するシステムを作成しました．問題点として，アラート件数の数に応じてチケットが作られてしまうので，今後は重複排除の機能を入れます．




