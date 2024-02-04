# yamaphoto
ヤマレコのログから写真とGPSログをバックアップするためのツールです。
**2024/1/30のヤマレコサイトデザイン変更に対応しました**

ヤマレコのログはヤマレコのメニューからcsv形式にバックアップできるのですが、写真とGPSログは手動で取得する必要があります。
特に写真の元サイズのデータを一つ一つ取ってくるのは大変なので、pythonでスクレイピングの勉強がてら作ってみました。
コマンドラインでもGUIでも使えます。取得が終わるとHTMLファイルができるのでブラウザで開くと元サイズの写真とそれぞれのキャプションを確認できます。
このままだと写真データはyamarecoのサイトのものをリンクしているだけですが、コマンドラインでは -l オプション、GUIは "save image locally" のチェックをつけると、htmlを保存したフォルダの下に photos-xxxxxx というフォルダを掘って、そこに001.jpgから順の名前で写真データを保存します。htmlファイルと同じフォルダにはGPSログ（GPXファイル）も保存します。またレコに記載したそのほかの情報は info-XXXXXX.txt (XXXXXX は記録ID）に保存されます。

なおログインしないと見れないログ（***ヤマレコ限定***とあるもの）からはバックアップできません。認証のためにはOAuthを使うのですが、現在は個人ベース等のアプリケーションではOAuth登録ができないようです。

## コマンドラインでの使い方

    yamaphoto.exe -u URL -d DIR [ -l ] [ -p PROXY ]

URLはヤマレコのログのURL、DIRは保存するフォルダパス（pythonなのでディレクトリのセパレータは "/" もしくは "\\\\" としてください。例えば c:/Temp とか。）
URLもしくはDIRが指定されない場合はGUIで立ち上がります。
-p でプロキシーサーバーを指定できます。プロキシーサーバーは環境変数（HTTP_PXORY, HTTPS_PROXY, FTP_PROXY) でも設定することができます。（コマンドオプション優先）
