# Musictaker

Discord上で使える音楽botです。  
Discordのボイスチャット内で音楽がほしいときにどうぞ。


# Features

現在対応しているのはsoundcloudとURLによるm3u8直指定での曲再生です。

# Requirement

このbotを動作させるには以下の物が必要です。  

* youtube-dl
* ffmpeg
* Discord.py（voice用ライブラリも必要)

# Installation

必要なライブラリをインストールした後secryt.pyをダウンロードして、  
コード内のTOKEN欄にあなたのbotのTOKENを入力すればそのまま利用できます。

# Usage

$play URL指定で音楽をプレイリストに追加  
$skip 現在再生中の曲をスキップ  
$now 現在再生中の曲を表示  
$remove 再生リストから曲を削除  
$queue 現在のプレイリストを表示  
$disconnect ボイスちゃんねるから切断  
$clear プレイリスト  

# Note
youtubeの規約によりyoutubeの動画は未対応となっています。  
soundcloudとURLによるm3u8の直接指定に対応しています。  


# License

使用しているライブラリのライセンスは以下の通りです。  
Discord.py [MIT license](https://en.wikipedia.org/wiki/MIT_License)  
ffmpeg [LGPL licence](https://en.wikipedia.org/wiki/GNU_Lesser_General_Public_License)  
youtube-dl　[Unlicense](https://en.wikipedia.org/wiki/Unlicense)  
