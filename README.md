# yamaphoto
ヤマレコのログから写真とGPSログをバックアップするためのツールです。
ヤマレコのログはヤマレコのメニューからcsv形式にバックアップできるのですが、写真とGPSログは手動で取得する必要があります。
特に写真の元サイズのデータを一つ一つ取ってくるのは大変なので、pythonでスクレイピングの勉強がてら作ってみました。
コマンドラインでもGUIでも使えます。取得が終わるとHTMLファイルができるのでブラウザで開くと元サイズの写真とそれぞれのキャプションを確認できます。
このままだと写真データはyamarecoのサイトのものをリンクしているだけですが、コマンドラインでは -l オプション、GUIは "save image locally" のチェックをつけると、htmlを保存したフォルダの下に photos-xxxxxx というフォルダを掘って、そこに001.jpgから順の名前で写真データを保存します。htmlfileと同じフォルダにはGPXファイルも保存します。

プロキシーも使うことができますが、GUIで対応するのが面倒なのでPythonのソースコード中の設定を変更する必要があります。需要があったらちゃんとやりますが…
またログインしないと見れないログからはバックアップできません。認証もできなくはないのですが、OAuth使うので色々めんどくさいのでやりません。

コマンドラインでの使い方
  yamaphoto.exe -u URL -d DIR (-l)
    URLはヤマレコのログのURL、DIRは保存するフォルダパス（pythonなのでディレクトリのセパレータは "/" もしくは "\\" としてください。例えば c:/Temp とか。
    URLもしくいはDIRが指定されない場合はGUIで立ち上がります。
