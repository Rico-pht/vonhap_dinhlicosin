import streamlit as st
import google.generativeai as genai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# 1. Cấu hình giao diện
st.set_page_config(page_title="Vở Nháp AI", page_icon="📐", layout="wide")

# 2. CSS TỔNG HỢP (Banner + Khung chat nổi góc phải)
st.markdown("""
<style>
/* Ẩn menu mặc định */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
/* --- TÙY CHỈNH THANH CUỘN (SCROLLBAR) CHO ĐIỆN THOẠI (BẢN SIÊU TO) --- */
::-webkit-scrollbar {
    width: 35px !important; /* Tăng bề ngang lên gấp đôi để ngón tay dễ chạm */
    background-color: #f4f6f8;
}
::-webkit-scrollbar-track {
    background-color: #f4f6f8; 
}
::-webkit-scrollbar-thumb {
    background-color: #999999; /* Đổi màu đậm hơn một chút để dễ nhìn thấy trên điện thoại */
    border-radius: 20px; /* Bo tròn xoe cho đẹp */
    border: 8px solid #f4f6f8; /* Viền siêu dày để thanh cuộn nhìn không quá thô nhưng VÙNG CHẠM thì rất to */
}
::-webkit-scrollbar-thumb:active {
    background-color: #666666; /* Khi ngón tay bấm vào sẽ đổi màu đậm hơn để báo hiệu */
}
/* --- CSS CHO BANNER --- */
.hero-banner {
    background-color: #2b3a4a; 
    padding: 45px 20px;
    text-align: center;
    border-radius: 10px;
    margin-bottom: 25px;
}
.hero-banner h1 {
    color: #ffffff;
    font-size: 40px;
    font-weight: bold;
    margin: 0;
    font-family: sans-serif;
    white-space: nowrap;
    overflow: hidden;
}

/* --- CSS CHO KHUNG CHAT NỔI (CĂN PHẢI TUYỆT ĐỐI) --- */
[data-testid="stExpander"] {
    position: fixed !important;
    bottom: 15px !important;
    right: 15px !important;
    left: auto !important; 
    width: auto !important; 
    z-index: 99999;
}
[data-testid="stExpander"] details {
    box-shadow: 0px 8px 24px rgba(0,0,0,0.15);
    transition: all 0.3s ease-in-out;
}

/* KHI ĐÓNG: BONG BÓNG TRÒN VIỀN ĐỎ */
[data-testid="stExpander"] details:not([open]) {
    width: 65px !important;
    height: 65px !important;
    border-radius: 50% !important;
    background-color: transparent !important;
    border: none !important;
}
[data-testid="stExpander"] details:not([open]) summary {
    background-color: #ffffff;
    border: 2px solid #ea1e24;
    border-radius: 50% !important;
    height: 65px;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0;
    list-style: none;
}
[data-testid="stExpander"] details:not([open]) summary::-webkit-details-marker {
    display: none;
}
[data-testid="stExpander"] details:not([open]) summary > * {
    display: none !important;
}
[data-testid="stExpander"] details:not([open]) summary::after {
    content: "🤖"; 
    font-size: 32px;
}

/* KHI MỞ: KHUNG CHAT CHỮ NHẬT */
[data-testid="stExpander"] details[open] {
    width: 380px !important;
    max-width: 90vw;
    background-color: #ffffff;
    border-radius: 12px !important;
    border: 1px solid #ddd;
    overflow: hidden;
}
[data-testid="stExpander"] details[open] summary {
    background-color: #ea1e24; 
    color: white !important;
    padding: 12px 15px;
    border-radius: 12px 12px 0 0 !important;
}
[data-testid="stExpanderDetails"] {
    max-height: 60vh;
    overflow-y: auto;
    padding: 15px;
}
.user-msg {
    background-color: #ea1e24;
    color: white;
    padding: 10px 14px;
    border-radius: 14px 14px 0 14px;
    margin-bottom: 12px;
    text-align: left;
    width: fit-content;
    max-width: 85%;
    margin-left: auto;
    font-size: 14px;
}
.ai-msg {
    background-color: #f1f2f6;
    color: #333;
    padding: 10px 14px;
    border-radius: 14px 14px 14px 0;
    margin-bottom: 12px;
    width: fit-content;
    max-width: 90%;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# 3. HIỂN THỊ BANNER & TIÊU ĐỀ
st.markdown("""
<style>
.hero-banner {
    background-color: #2b3a4a; 
    padding: 25px 15px;
    text-align: center;
    border-radius: 10px;
    margin-bottom: 25px;
}
.hero-banner .title-sub {
    color: #FFD700; 
    font-size: 28px; 
    font-weight: bold;
    margin: 0;
    font-family: sans-serif;
}
.hero-banner h1 {
    color: #ffffff;
    font-size: 24px; /* Đã thu nhỏ chữ lại */
    font-weight: bold;
    margin: 5px 0 0 0;
    font-family: sans-serif;
    /* ĐÃ XÓA LỆNH ÉP 1 DÒNG Ở ĐÂY ĐỂ CHỮ TỰ ĐỘNG XUỐNG HÀNG TRÊN ĐIỆN THOẠI */
}
@media (min-width: 600px) {
    .hero-banner .title-sub { font-size: 40px; }
    .hero-banner h1 { font-size: 40px; }
}
</style>

<div class="hero-banner">
    <div class="title-sub">Vở Nháp</div>
    <h1>Định lí côsin và Định lí sin</h1>
</div>
""", unsafe_allow_html=True)


# 4. CẤU HÌNH AI
api_key = "AQ.Ab8RN6LiMbBJYmjpHhWOpITmihkz0Zs29eWkv1bPBhSXIJ90eg"

# Khởi tạo thẳng AI phiên bản mới nhất (flash-latest) để không bị lỗi 404
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.6-flash')

system_prompt = """
Bạn là gia sư Toán học dạy theo phương pháp kiến tạo. Chuyên môn: Định lí Côsin và Định lí Sin.
Nhiệm vụ: Đọc nét vẽ trực tiếp từ bảng vẽ của học sinh, phân tích đúng sai.
Tuyệt đối KHÔNG đưa ra đáp án, chỉ đặt câu hỏi gợi mở để học sinh tự tìm ra cách giải.
"""

# 5. KHU VỰC BẢNG VẼ MÃ NGUỒN MỞ

# Yêu cầu 1: Độ dày nét bút dạng bấm chọn, nằm gọn gàng trên cùng
thickness_choice = st.selectbox("📏 Chọn độ dày nét bút:", ("Nhỏ", "Vừa", "Dày", "Rất dày"))
thickness_map = {"Nhỏ": 2, "Vừa": 4, "Dày": 8, "Rất dày": 12}
stroke_width = thickness_map[thickness_choice]

# Chia 2 cột cho Màu sắc và Công cụ
col1, col2 = st.columns(2)

with col1:
    # Cột 1 (Màu bút) sẽ tự động nằm bên trên khi xem bằng điện thoại
    color_choice = st.radio(
        "🎨 Màu bút:", 
        ("⬛", "🟥", "🟦", "🟩", "🟨"), 
        horizontal=True
    )

with col2:
    # Cột 2 (Công cụ) sẽ nằm bên dưới
    tool_choice = st.radio(
        "🛠️ Công cụ:", 
        ("🖌️", "📏", "⭕", "🖱️", "⌫"),
        horizontal=True
    )

# Bộ từ điển chuyển đổi từ Emoji sang Mã màu chuẩn (Hex)
color_map = {
    "⬛": "#000000", # Đen
    "🟥": "#ea1e24", # Đỏ
    "🟦": "#3b82f6", # Xanh dương
    "🟩": "#22c55e", # Xanh lá
    "🟨": "#eab308"  # Vàng
}
selected_color = color_map[color_choice]

# Xử lý logic phía sau cho từng công cụ
if tool_choice == "🖌️":
    drawing_mode = "freedraw"
    active_color = selected_color
elif tool_choice == "📏":
    drawing_mode = "line"
    active_color = selected_color
elif tool_choice == "⭕":
    drawing_mode = "circle"
    active_color = selected_color
elif tool_choice == "🖱️":
    drawing_mode = "transform"
    active_color = selected_color
elif tool_choice == "⌫":
    drawing_mode = "freedraw"
    active_color = "#f9f9f9" # Bí kíp: Biến màu bút thành màu nền
    stroke_width = stroke_width + 15 # Nét tẩy tự động to lên để HS dễ xóa

# Khởi tạo bảng vẽ
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)", 
    stroke_width=stroke_width,
    stroke_color=active_color, # Đã đồng bộ màu với logic ở trên
    background_color="#f9f9f9",
    update_streamlit=True,
    height=450,
    drawing_mode=drawing_mode,
    key="canvas",
)

# 6. KHUNG CHAT AI TRÔI NỔI
if "messages" not in st.session_state:
    st.session_state.messages = []

# Đã đổi tên thành "Trợ lí thầy Trung" và để mặc định đóng (expanded=False)
with st.expander("💬 Trợ lí thầy Trung", expanded=False):
    
    if not st.session_state.messages:
        st.markdown('<div class="ai-msg">👋 Chào thầy và các em! Hãy vẽ phác thảo ra bảng rồi đặt câu hỏi, tôi sẽ nhìn trực tiếp nét vẽ để hướng dẫn nhé!</div>', unsafe_allow_html=True)
        
    for msg in st.session_state.messages:
        # Sử dụng giao diện chat mặc định của Streamlit để dịch mượt mà công thức Toán
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("---")
    
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Hỏi trợ lí AI...", placeholder="Thầy ơi xem giúp em hình này...")
        submit_button = st.form_submit_button("Gửi tin nhắn 🚀", use_container_width=True)

        if submit_button and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            content_to_send = [system_prompt, user_input]
            
            # ĐIỂM ĂN TIỀN: Lấy hình ảnh trực tiếp từ Canvas gửi thẳng cho AI
            if canvas_result.image_data is not None:
                canvas_image = Image.fromarray((canvas_result.image_data).astype(np.uint8))
                content_to_send.append(canvas_image)
                
            try:
                if api_key == "ĐIỀN_API_KEY_CỦA_BẠN_VÀO_ĐÂY":
                    st.session_state.messages.append({"role": "assistant", "content": "Vui lòng điền API Key vào mã nguồn."})
                else:
                    with st.spinner("Đang nhìn bảng vẽ..."):
                        response = model.generate_content(content_to_send)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Lỗi: {e}"})
            
            st.rerun()