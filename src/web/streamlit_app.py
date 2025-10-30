import streamlit as st
import os
import subprocess
import json
import time
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="매일경제 AI 플랫폼",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# React 앱 서빙을 위한 HTML
def serve_react_app():
    st.markdown("""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="utf-8" />
        <link rel="icon" href="/static/favicon.ico" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#000000" />
        <meta name="description" content="매일경제 AI 벡터임베딩 플랫폼" />
        <title>매일경제 AI 플랫폼</title>
        <style>
            body {
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
                    sans-serif;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
            code {
                font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
                    monospace;
            }
            #root {
                height: 100vh;
            }
        </style>
    </head>
    <body>
        <noscript>You need to enable JavaScript to run this app.</noscript>
        <div id="root"></div>
        <script src="/static/js/main.728b4b84.js"></script>
        <script src="/static/js/453.d7446e4a.chunk.js"></script>
    </body>
    </html>
    """, unsafe_allow_html=True)

def main():
    # React 앱 서빙
    serve_react_app()

if __name__ == "__main__":
    main()