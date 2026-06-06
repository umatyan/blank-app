import streamlit as st
import pytchat
import re
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd

st.title("🎬 VTuber切り抜き支援ツール")
st.write("YouTubeのURLを入れるだけで、盛り上がったシーンを自動で見つけます！")

# 初期設定のURL自体を、リヴィさんが今使っている本物のURLに変えました！
youtube_url = st.text_input(
    "解析したいYouTube動画のURLを入力してください", 
    "https://www.youtube.com/watch?v=60jKLr6RbVo"
)

mode = st.radio("解析モードを選択してください", ["📝 本人の喋り（字幕）から探す", "💬 チャット欄から探す"])

# どんなURLが来ても、後ろの11文字（動画ID）だけを確実に引き抜く頑丈な処理
def extract_video_id(url):
    if not url:
        return None
    if "v=" in url:
        return url.split("v=")[1][:11]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1][:11]
    return url[-11:]

video_id = extract_video_id(youtube_url)

if st.button("🚀 解析をスタート"):
    if not video_id:
        st.error("有効なYouTubeのURLを入力してください。")
    else:
        st.info(f"動画ID: {video_id} を解析中...")
        
        if "字幕" in mode:
            try:
                # 日本語字幕を確実に取得
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja'])
                if transcript:
                    df = pd.DataFrame(transcript)
                    df['秒数'] = df['start'].astype(int)
                    st.success("✅ 文字起こしデータの取得に成功しました！")
                    st.dataframe(df[['秒数', 'text']].rename(columns={'text': '喋った内容'}))
                else:
                    st.warning("⚠️ 字幕データが空っぽでした。")
            except Exception as e:
                st.error(f"❌ 字幕の取得に失敗しました。理由: {str(e)}")
                
        else:
            try:
                chat = pytchat.create(video_id=video_id, interruptable=False)
                chat_list = []
                for i in range(5):
                    if chat.is_alive():
                        for c in chat.get().sync_items():
                            chat_list.append({"時間": c.elapsedTime, "コメント": c.message, "ユーザー": c.author.name})
                if chat_list:
                    df = pd.DataFrame(chat_list)
                    st.success("✅ チャットデータの取得に成功しました！")
                    st.dataframe(df)
                else:
                    st.warning("⚠️ チャットが読み込めませんでした。ライブ配信のアーカイブでお試しください。")
            except Exception as e:
                st.error(f"❌ チャットの取得に失敗しました。理由: {str(e)}")