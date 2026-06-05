import streamlit as st
import pytchat
import re
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd

# アプリのタイトル
st.title("🎬 VTuber切り抜き支援ツール")
st.write("YouTubeのURLを入れるだけで、盛り上がったシーンを自動で見つけます！")

# 1. URLの入力欄
youtube_url = st.text_input("解析したいYouTube動画のURLを入力してください", "https://www.youtube.com/watch?v=eoYtgL7zHJg")

# 2. 解析方法の選択（チャットがダメなら字幕にすぐ切り替えられる二段構え）
mode = st.radio("解析モードを選択してください", ["💬 チャット欄から探す", "📝 本人の喋り（字幕）から探す"])

# URLから動画IDを抜き出す処理
def extract_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

video_id = extract_video_id(youtube_url)

# 3. 解析ボタン
if st.button("🚀 解析をスタート"):
    if not video_id:
        st.error("有効なYouTubeのURLを入力してください。")
    else:
        st.info(f"動画ID: {video_id} を解析中... 少々お待ちください。")
        
        # --- チャットモード ---
        if "チャット" in mode:
            try:
                chat = pytchat.create(video_id=video_id)
                chat_list = []
                
                # 最初の一部をテスト取得
                for i in range(10):
                    if chat.is_alive():
                        for c in chat.get().sync_items():
                            chat_list.append({"時間": c.elapsedTime, "コメント": c.message, "ユーザー": c.author.name})
                
                if chat_list:
                    df = pd.DataFrame(chat_list)
                    st.success(f"✅ チャットデータの取得に成功しました！（テスト表示）")
                    st.dataframe(df)
                else:
                    st.warning("⚠️ チャットがうまく読み込めませんでした。『字幕モード』を試してみてください！")
            except Exception as e:
                st.error(f"エラーが発生しました。字幕モードをお試しください。")
                
        # --- 字幕モード ---
        else:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja'])
                df = pd.DataFrame(transcript)
                
                st.success("✅ 文字起こしデータの取得に成功しました！")
                # 見やすいように整形
                df['秒数'] = df['start'].astype(int)
                st.dataframe(df[['秒数', 'text']].rename(columns={'text': '喋った内容'}))
                
            except Exception as e:
                st.error("❌ 字幕データの取得に失敗しました。この動画には字幕が設定されていない可能性があります。")