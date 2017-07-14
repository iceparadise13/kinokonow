### インストール
```
pip install -r requirements.txt
```

### 実行
ストリーム
```
python -m listen
```
ワーカー
```
celery -A tasks.celery -l INFO worker
```
定期ツイート
```
celery -A tasks.celery -l INFO beat
```

### LICENSE

wordcloud2.js  
Tag cloud/Wordle presentation on 2D canvas or HTML  
url: https://github.com/timdream/wordcloud2.js  
license : MIT
