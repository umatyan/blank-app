import streamlit as st
import pytchat
import re
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd

st.title("🎬 VTuber切り抜き支援ツール")
st.write("YouTubeのURLを入れるだけで、盛り上がったシーンを自動で見つけます！")

# 1. URLの入力欄（最初から確実にデータがある動画のURLをセットしておきます）
youtube_url = st.text_input(
    "解析したいYouTube動画のURLを入力してください", 
    "https://www.youtube.com/watch?v=A4gX7_Y7f2M"
)

mode = st.radio("解析モードを選択してください", ["💬 チャット欄から探す", "📝 本人の喋り（字幕）から探す"])

# URLから動画IDを安全に抜き出す処理
def extract_video_id(url):
    if not url:
        return None
    # いろんなURLの形式（通常、スマホ用、ショート等）に対応
    patterns = [
        r'v=([^#\&\?]+)',
        r'youtu\.be/([^#\&\?]+)',
        r'embed/([^#\&\?]+)',
        r'/shorts/([^#\&\?]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

video_id = extract_video_id(youtube_url)

if st.button("🚀 解析をスタート"):
    if not video_id:
        st.error("有効なYouTubeのURLを入力してください。")
    else:
        st.info(f"動画ID: {video_id} を解析中...")
        
        # --- 字幕モード ---
        if "字幕" in mode:
            try:
                # 言語を日本語（ja）に指定して取得
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja'])
                
                if transcript:
                    df = pd.DataFrame(transcript)
                    df['秒数'] = df['start'].astype(int)
                    
                    st.success("✅ 文字起こしデータの取得に成功しました！")
                    st.dataframe(df[['秒数', 'text']].rename(columns={'text': '喋った内容'}))
                else:
                    st.warning("⚠️ 字幕データが空っぽでした。")
                    
            except Exception as e:
                # どんなエラーが起きているか画面に詳しく出すように強化
                st.error(f"❌ 字幕の取得に失敗しました。理由: {str(e)}")
                st.info("※自動字幕の生成がまだ完了していない動画、または外部からの取得が制限されている動画の可能性があります。")
                
        # --- チャットモード ---
        else:
            try:
                chat = pytchat.create(video_id=video_id)
                chat_list = []
                
                # テスト用に少しだけチャットを引っ張る
                for i in range(5):
                    if chat.is_alive():
                        for c in chat.get().sync_items():
                            chat_list.append({"時間": c.elapsedTime, "コメント": c.message, "ユーザー": c.author.name})
                
                if chat_list:
                    df = pd.DataFrame(chat_list)
                    st.success("✅ チャットデータの取得に成功しました！")
                    st.dataframe(df)
                else:
                    st.warning("⚠️ チャットがうまく読み込めませんでした。ライブ配信のアーカイブ（チャットリプレイがある動画）でお試しください。")
            except Exception as e:
                st.error(f"❌ チャットの取得に失敗しました。理由: {str(e)}")